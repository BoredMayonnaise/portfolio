"""Responsive image generation shared by all public image models."""

import hashlib
from io import BytesIO

from PIL import Image, ImageOps


RESPONSIVE_WIDTHS = (480, 960, 1600)
WEBP_QUALITY = 82


def _variant_names(metadata):
    return {
        variant.get("name")
        for variant in (metadata or {}).get("variants", [])
        if variant.get("name")
    }


def delete_image_variants(storage, metadata, keep=()):
    """Delete generated files recorded in metadata, except paths in ``keep``."""
    keep = set(keep)
    for name in _variant_names(metadata) - keep:
        try:
            storage.delete(name)
        except OSError:
            # A missing derivative must not prevent an image/model update.
            pass


def generate_image_variants(instance, force=False):
    """Generate content-hashed WebP derivatives and return their metadata."""
    image_field = instance.image
    if not image_field or not image_field.name:
        return {}

    storage = image_field.storage
    try:
        with storage.open(image_field.name, "rb") as source:
            source_bytes = source.read()
    except (OSError, ValueError):
        return {}

    digest = hashlib.sha256(source_bytes).hexdigest()
    current = instance.image_variants or {}
    current_names = _variant_names(current)
    if (
        not force
        and current.get("source_hash") == digest
        and current_names
        and all(storage.exists(name) for name in current_names)
    ):
        return current

    try:
        with Image.open(BytesIO(source_bytes)) as opened:
            source_image = ImageOps.exif_transpose(opened)
            source_image.load()
    except (OSError, ValueError):
        return {}

    source_width, source_height = source_image.size
    if not source_width or not source_height:
        return {}

    has_alpha = source_image.mode in ("RGBA", "LA") or (
        source_image.mode == "P" and "transparency" in source_image.info
    )
    working_image = source_image.convert("RGBA" if has_alpha else "RGB")
    widths = sorted({min(source_width, width) for width in RESPONSIVE_WIDTHS})
    variants = []

    for width in widths:
        height = max(1, round(source_height * width / source_width))
        if (width, height) == working_image.size:
            resized = working_image.copy()
        else:
            resized = working_image.resize((width, height), Image.Resampling.LANCZOS)

        output = BytesIO()
        resized.save(
            output,
            format="WEBP",
            quality=WEBP_QUALITY,
            method=6,
        )
        output.seek(0)

        name = f"variants/{instance._meta.model_name}/{digest}/{width}.webp"
        if force and storage.exists(name):
            storage.delete(name)
        if not storage.exists(name):
            saved_name = storage.save(name, output)
        else:
            saved_name = name

        variants.append({"width": width, "height": height, "name": saved_name})

    return {
        "source_hash": digest,
        "source_width": source_width,
        "source_height": source_height,
        "variants": variants,
    }


class ResponsiveImageMixin:
    """Model behavior for generating and exposing responsive derivatives."""

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.ensure_image_variants()

    def ensure_image_variants(self, force=False):
        old_metadata = self.image_variants or {}
        new_metadata = generate_image_variants(self, force=force)
        if new_metadata != old_metadata:
            type(self).objects.filter(pk=self.pk).update(image_variants=new_metadata)
            self.image_variants = new_metadata
            delete_image_variants(
                self.image.storage,
                old_metadata,
                keep=_variant_names(new_metadata),
            )
        return new_metadata

    @property
    def responsive_srcset(self):
        if not self.image:
            return ""
        storage = self.image.storage
        return ", ".join(
            f"{storage.url(variant['name'])} {variant['width']}w"
            for variant in self.image_variants.get("variants", [])
            if variant.get("name") and variant.get("width")
        )

    def _variant_url(self, preferred_width=None):
        if not self.image:
            return ""
        variants = self.image_variants.get("variants", [])
        if not variants:
            return self.image.url
        ordered = sorted(variants, key=lambda variant: variant["width"])
        if preferred_width is None:
            selected = ordered[-1]
        else:
            selected = next(
                (variant for variant in ordered if variant["width"] >= preferred_width),
                ordered[-1],
            )
        return self.image.storage.url(selected["name"])

    @property
    def responsive_url(self):
        return self._variant_url(preferred_width=960)

    @property
    def lightbox_url(self):
        return self._variant_url()
