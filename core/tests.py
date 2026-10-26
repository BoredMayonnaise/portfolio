import json
import tempfile
from io import BytesIO
from unittest.mock import patch

from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import Client, TestCase, override_settings
from PIL import Image

from .brief import (
    FORK_QUESTION,
    TRACK_A_QUESTIONS,
    TRACK_B_QUESTIONS,
    TRACK_OPERATIONAL,
    TRACK_PRODUCT,
)
from .models import BriefResponse, ContactMessage, Project

TRACK_A_ANSWERS = {
    "track": TRACK_OPERATIONAL,
    **{
        q["id"]: (list(q["options"]) if q.get("multi") else q["options"][0])
        for q in TRACK_A_QUESTIONS
    },
}

TRACK_B_ANSWERS = {
    "track": TRACK_PRODUCT,
    **{
        q["id"]: (list(q["options"]) if q.get("multi") else q["options"][0])
        for q in TRACK_B_QUESTIONS
    },
}


class BriefSubmissionTests(TestCase):
    @override_settings(
        CONTACT_TO_EMAIL="admin@example.com",
        DEFAULT_FROM_EMAIL="no-reply@example.com",
    )
    def test_custom_business_email_domain_is_accepted(self):
        payload = {
            "email": "Founder@Acme.Studio",
            "answers": TRACK_B_ANSWERS,
            "honeypot": "",
        }
        response = self.client.post(
            "/brief/submit/",
            data=json.dumps(payload),
            secure=True,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"ok": True})
        self.assertTrue(BriefResponse.objects.filter(email="founder@acme.studio").exists())

    @override_settings(
        CONTACT_TO_EMAIL="admin@gmail.com",
        DEFAULT_FROM_EMAIL="no-reply@example.com",
    )
    def test_valid_track_a_submission_saves_and_sends_both_emails(self):
        payload = {"email": "client@gmail.com", "answers": TRACK_A_ANSWERS, "honeypot": ""}
        response = self.client.post(
            "/brief/submit/",
            data=json.dumps(payload), secure=True,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"ok": True})

        saved = BriefResponse.objects.get(email="client@gmail.com")
        self.assertTrue(saved.admin_notified)
        self.assertTrue(saved.thank_you_sent)
        self.assertEqual(saved.answers["track"], TRACK_OPERATIONAL)

        self.assertEqual(len(mail.outbox), 2)
        admin_email, client_email = mail.outbox
        self.assertIn("admin@gmail.com", admin_email.to)
        self.assertIn("90-second brief", admin_email.subject)
        self.assertEqual(client_email.to, ["client@gmail.com"])
        self.assertIn("Thank you for sharing your problem", client_email.body)
        self.assertEqual(len(client_email.alternatives), 1)
        html, mime = client_email.alternatives[0]
        self.assertEqual(mime, "text/html")
        self.assertIn("Thank you for sharing your problem", html)
        self.assertNotIn("INDEPENDENT WEB ENGINEER", html)
        self.assertNotIn("independent web engineer", client_email.body)

    @override_settings(
        CONTACT_TO_EMAIL="admin@gmail.com",
        DEFAULT_FROM_EMAIL="no-reply@example.com",
    )
    def test_valid_track_b_submission_saves_and_sends_product_emails(self):
        mail.outbox.clear()
        payload = {"email": "founder@gmail.com", "answers": TRACK_B_ANSWERS, "honeypot": ""}
        response = self.client.post(
            "/brief/submit/",
            data=json.dumps(payload), secure=True,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"ok": True})

        saved = BriefResponse.objects.get(email="founder@gmail.com")
        self.assertTrue(saved.admin_notified)
        self.assertTrue(saved.thank_you_sent)
        self.assertEqual(saved.answers["track"], TRACK_PRODUCT)
        self.assertIn("app_type", saved.answers)

        self.assertEqual(len(mail.outbox), 2)
        admin_email, client_email = mail.outbox
        self.assertIn("admin@gmail.com", admin_email.to)
        self.assertIn("project brief", admin_email.subject)
        self.assertEqual(client_email.to, ["founder@gmail.com"])
        self.assertIn("Thank you for sharing your project", client_email.body)
        self.assertNotIn("problem", client_email.body.lower())
        self.assertEqual(len(client_email.alternatives), 1)
        html, mime = client_email.alternatives[0]
        self.assertEqual(mime, "text/html")
        self.assertIn("Thank you for sharing your project", html)
        self.assertNotIn("INDEPENDENT WEB ENGINEER", html)
        self.assertNotIn("independent web engineer", client_email.body)

    def test_track_b_questions_completely_different_from_track_a(self):
        track_a_ids = {q["id"] for q in TRACK_A_QUESTIONS}
        track_b_ids = {q["id"] for q in TRACK_B_QUESTIONS}
        # Check there is zero question ID overlap
        self.assertEqual(track_a_ids.intersection(track_b_ids), set())

        # Submitting Track A questions with Track B selected must fail validation
        mismatched_answers = {
            "track": TRACK_PRODUCT,
            **{
                q["id"]: (list(q["options"]) if q.get("multi") else q["options"][0])
                for q in TRACK_A_QUESTIONS
            },
        }
        payload = {"email": "client@gmail.com", "answers": mismatched_answers, "honeypot": ""}
        response = self.client.post(
            "/brief/submit/",
            data=json.dumps(payload), secure=True,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(response.json()["ok"])

    @override_settings(CONTACT_TO_EMAIL="", DEFAULT_FROM_EMAIL="no-reply@example.com")
    def test_submission_without_admin_recipient_saves_and_still_thanks_client(self):
        mail.outbox.clear()
        payload = {"email": "client@gmail.com", "answers": TRACK_A_ANSWERS, "honeypot": ""}
        response = self.client.post(
            "/brief/submit/",
            data=json.dumps(payload), secure=True,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        saved = BriefResponse.objects.get(email="client@gmail.com")
        self.assertFalse(saved.admin_notified)
        self.assertTrue(saved.thank_you_sent)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["client@gmail.com"])


class ResponsiveImageTests(TestCase):
    def setUp(self):
        self.media_dir = tempfile.TemporaryDirectory()
        self.settings_override = override_settings(MEDIA_ROOT=self.media_dir.name)
        self.settings_override.enable()

    def tearDown(self):
        self.settings_override.disable()
        self.media_dir.cleanup()

    @staticmethod
    def image_upload(name="source.jpg", size=(2000, 1000), mode="RGB", fmt="JPEG"):
        output = BytesIO()
        color = (35, 95, 70, 180) if mode == "RGBA" else (35, 95, 70)
        Image.new(mode, size, color).save(output, format=fmt)
        return SimpleUploadedFile(
            name,
            output.getvalue(),
            content_type=f"image/{fmt.lower()}",
        )

    def create_project(self, **kwargs):
        defaults = {
            "title": "Responsive project",
            "description": "An image variant test project.",
            "tech_stack": "Django",
            "featured": True,
            "image": self.image_upload(),
        }
        defaults.update(kwargs)
        return Project.objects.create(**defaults)

    def test_upload_keeps_original_and_generates_webp_sizes(self):
        project = self.create_project()

        self.assertTrue(project.image.name.endswith(".jpg"))
        variants = project.image_variants["variants"]
        self.assertEqual([item["width"] for item in variants], [480, 960, 1600])
        self.assertIn("480w", project.responsive_srcset)
        self.assertIn("1600w", project.responsive_srcset)

        with project.image.storage.open(project.image.name, "rb") as original:
            with Image.open(original) as image:
                self.assertEqual(image.format, "JPEG")
                self.assertEqual(image.size, (2000, 1000))

        for item in variants:
            with project.image.storage.open(item["name"], "rb") as derivative:
                with Image.open(derivative) as image:
                    self.assertEqual(image.format, "WEBP")
                    self.assertEqual(image.size, (item["width"], item["height"]))

    def test_small_images_are_not_upscaled(self):
        project = self.create_project(
            title="Small project",
            image=self.image_upload(size=(320, 180)),
        )

        variants = project.image_variants["variants"]
        self.assertEqual(len(variants), 1)
        self.assertEqual(variants[0]["width"], 320)
        self.assertEqual(variants[0]["height"], 180)

    def test_transparent_png_keeps_its_alpha_channel(self):
        project = self.create_project(
            title="Transparent project",
            image=self.image_upload(
                name="transparent.png",
                size=(600, 400),
                mode="RGBA",
                fmt="PNG",
            ),
        )

        largest = project.image_variants["variants"][-1]
        with project.image.storage.open(largest["name"], "rb") as derivative:
            with Image.open(derivative) as image:
                self.assertEqual(image.mode, "RGBA")
                self.assertEqual(image.getpixel((0, 0))[3], 180)

    def test_replacing_an_image_removes_obsolete_derivatives(self):
        project = self.create_project()
        old_names = [item["name"] for item in project.image_variants["variants"]]

        project.image = self.image_upload(name="replacement.png", size=(1200, 1200), fmt="PNG")
        project.save()

        self.assertTrue(project.image.name.endswith(".png"))
        self.assertEqual(
            [item["width"] for item in project.image_variants["variants"]],
            [480, 960, 1200],
        )
        self.assertTrue(all(not project.image.storage.exists(name) for name in old_names))

    def test_backfill_command_restores_missing_variants(self):
        project = self.create_project()
        for item in project.image_variants["variants"]:
            project.image.storage.delete(item["name"])
        Project.objects.filter(pk=project.pk).update(image_variants={})

        call_command("generate_image_variants")

        project.refresh_from_db()
        self.assertEqual(
            [item["width"] for item in project.image_variants["variants"]],
            [480, 960, 1600],
        )

    def test_homepage_renders_responsive_image_markup(self):
        project = self.create_project()

        response = self.client.get("/", secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "srcset=")
        self.assertContains(response, "sizes=")
        self.assertContains(response, project.lightbox_url)

    def test_variant_responses_are_immutable_webp(self):
        project = self.create_project()

        response = self.client.get(project.responsive_url, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/webp")
        self.assertEqual(
            response["Cache-Control"],
            "public, max-age=31536000, immutable",
        )

    def test_deleting_an_image_record_removes_its_derivatives(self):
        project = self.create_project()
        storage = project.image.storage
        variant_names = [item["name"] for item in project.image_variants["variants"]]

        project.delete()

        self.assertTrue(all(not storage.exists(name) for name in variant_names))


class ProjectCaseStudyTests(TestCase):
    def test_project_detail_renders_factual_case_study_sections(self):
        project = Project.objects.create(
            title="Case study",
            description="A concise project summary.",
            tech_stack="Django, SQLite",
            problem="A clearly defined product problem.",
            audience="The people affected by that problem.",
            role="Independent product design and engineering.",
            constraints="The delivery and technical constraints.",
            decisions="The important implementation decisions.",
            outcome="A factual, non-inflated outcome.",
            lessons="A concrete lesson from the work.",
        )

        response = self.client.get(project.get_absolute_url(), secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "THE PROBLEM")
        self.assertContains(response, "INTENDED FOR")
        self.assertContains(response, "MY ROLE")
        self.assertContains(response, "Constraints into")
        self.assertContains(response, "A factual, non-inflated outcome.")
        self.assertContains(response, "A concrete lesson from the work.")

    def test_blank_case_study_fields_do_not_render_empty_sections(self):
        project = Project.objects.create(
            title="Simple project",
            description="Only a project summary.",
            tech_stack="Django",
        )

        response = self.client.get(project.get_absolute_url(), secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "THE PROBLEM")
        self.assertNotContains(response, "Constraints into")
        self.assertNotContains(response, "Outcome &amp;")


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    ADMINS=[],
    CONTACT_TO_EMAIL="owner@example.com",
    DEFAULT_FROM_EMAIL="portfolio@example.com",
)
class ContactMessageTests(TestCase):
    def setUp(self):
        mail.outbox.clear()
        self.payload = {
            "name": "A visitor",
            "email": "Visitor@Example.com",
            "message": "I would like to discuss building a new website for my small business.",
            "honeypot": "",
        }

    def test_valid_message_saves_notifies_and_refresh_does_not_duplicate(self):
        response = self.client.post("/contact/", self.payload, secure=True)
        self.assertRedirects(response, "/contact/#message-status", fetch_redirect_response=False)
        saved = ContactMessage.objects.get()
        self.assertEqual(saved.email, "visitor@example.com")
        self.assertEqual(saved.ip, "127.0.0.1")
        self.assertEqual(mail.outbox[0].to, ["owner@example.com"])
        self.assertEqual(mail.outbox[0].reply_to, ["visitor@example.com"])
        self.assertIn(self.payload["message"], mail.outbox[0].body)
        self.client.get("/contact/", secure=True)
        self.assertEqual(ContactMessage.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)

    def test_invalid_message_keeps_values_and_explains_error(self):
        self.payload["message"] = "Too short"
        response = self.client.post("/contact/", self.payload, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Please write at least 10 words.")
        self.assertContains(response, 'value="A visitor"')
        self.assertContains(response, "Too short")
        self.assertContains(response, 'aria-invalid="true"')
        self.assertContains(response, 'aria-describedby="message-hint id_message_error"')
        self.assertFalse(ContactMessage.objects.exists())

    def test_invalid_email_is_rejected(self):
        self.payload["email"] = "invalid-address"
        response = self.client.post("/contact/", self.payload, secure=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter a valid email address.")
        self.assertFalse(ContactMessage.objects.exists())

    def test_honeypot_does_not_save_or_send(self):
        self.payload["honeypot"] = "spam"
        response = self.client.post("/contact/", self.payload, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(ContactMessage.objects.exists())
        self.assertEqual(len(mail.outbox), 0)

    def test_third_message_is_limited_but_another_ip_can_submit(self):
        for _ in range(2):
            self.assertEqual(self.client.post("/contact/", self.payload, secure=True).status_code, 302)
        response = self.client.post("/contact/", self.payload, secure=True)
        self.assertEqual(response.status_code, 429)
        self.assertContains(response, "Message limit reached", status_code=429)
        self.assertEqual(ContactMessage.objects.count(), 2)
        response = self.client.post("/contact/", self.payload, secure=True, REMOTE_ADDR="192.0.2.1")
        self.assertEqual(response.status_code, 302)

    def test_old_message_does_not_use_current_limit(self):
        from datetime import timedelta
        from django.utils import timezone
        for _ in range(2):
            message = ContactMessage.objects.create(
                name="Earlier visitor", email="earlier@example.com", message="Earlier message", ip="127.0.0.1"
            )
            ContactMessage.objects.filter(pk=message.pk).update(created_at=timezone.now() - timedelta(hours=2))
        self.assertEqual(self.client.post("/contact/", self.payload, secure=True).status_code, 302)

    def test_notification_failure_keeps_saved_message(self):
        with patch("core.views.EmailMultiAlternatives.send", side_effect=OSError("Mail unavailable")):
            with self.assertLogs("core.views", level="ERROR"):
                response = self.client.post("/contact/", self.payload, secure=True, follow=True)
        self.assertEqual(ContactMessage.objects.count(), 1)
        self.assertContains(response, "Message received.")
        self.assertNotContains(response, "Email sent")

    @override_settings(CONTACT_TO_EMAIL="")
    def test_missing_recipient_keeps_saved_message(self):
        with self.assertLogs("core.views", level="WARNING"):
            response = self.client.post("/contact/", self.payload, secure=True)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ContactMessage.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 0)

    def test_database_failure_shows_retry_without_claiming_success(self):
        from django.db import OperationalError
        with patch("core.views.ContactMessage.save", side_effect=OperationalError("Database locked")):
            with self.assertLogs("core.views", level="ERROR"):
                response = self.client.post("/contact/", self.payload, secure=True)
        self.assertContains(response, "Your message could not be saved", status_code=503)
        self.assertFalse(ContactMessage.objects.exists())
        self.assertEqual(len(mail.outbox), 0)

    def test_contact_post_requires_csrf(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post("/contact/", self.payload, secure=True)
        self.assertEqual(response.status_code, 403)
        page = client.get("/contact/", secure=True)
        payload = {**self.payload, "csrfmiddlewaretoken": page.cookies["csrftoken"].value}
        response = client.post("/contact/", payload, secure=True, HTTP_REFERER="https://testserver/contact/")
        self.assertEqual(response.status_code, 302)


class PortfolioClarityTests(TestCase):
    def test_public_metadata_and_discovery_use_current_domain(self):
        for path in ["/", "/projects/", "/blog/", "/contact/", "/sitemap.xml", "/robots.txt"]:
            with self.subTest(path=path):
                response = self.client.get(path, secure=True)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "https://markocampos.rhymvex.space")
                self.assertNotContains(response, "markocampos.duckdns.org")

    def test_homepage_exposes_identity_direct_links_and_project_evidence(self):
        project = Project.objects.create(
            title="Evidence project", description="A useful product for a real problem.",
            tech_stack="Python", role="Designer and engineer", outcome="Working product delivered",
        )
        response = self.client.get("/", secure=True)
        self.assertContains(response, "Independent web engineer")
        self.assertContains(response, 'href="/projects/"')
        self.assertContains(response, 'href="/contact/"')
        self.assertContains(response, project.description)
        self.assertContains(response, project.role)
        self.assertContains(response, project.outcome)
        self.assertNotContains(response, "95%")
        response = self.client.get("/projects/", secure=True)
        self.assertContains(response, project.description)
        self.assertContains(response, project.outcome)
