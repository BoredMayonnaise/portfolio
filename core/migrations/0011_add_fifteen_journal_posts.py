from datetime import datetime, timezone
from django.db import migrations
from django.utils.text import slugify

POSTS = [
    {
        "title": "Designing for SQLite in Production",
        "slug": "designing-for-sqlite-in-production",
        "created_at": datetime(2026, 8, 11, 14, 30, tzinfo=timezone.utc),
        "excerpt": "Why single-file databases punch well above their weight for focused, content-driven web applications.",
        "body": """Running SQLite in production used to raise eyebrows. For years, conventional wisdom dictated that any serious web application needed a standalone database server like PostgreSQL or MySQL running in a separate container or dedicated virtual machine.

For large distributed systems with dozens of concurrent write-heavy services, that separation makes sense. But for a personal studio, focused content platforms, and independent applications, SQLite offers significant architectural advantages:

- **Zero network round-trips:** Queries execute directly in process memory without TCP handshakes or socket serialization overhead.
- **Trivial backups:** Backing up your database is as straightforward as copying a single file or taking a point-in-time filesystem snapshot.
- **Minimal operational overhead:** No background database daemon to monitor, tune, patch, or restart after unexpected crashes.

### Enabling WAL Mode

The key to production SQLite is Write-Ahead Logging (WAL mode). By default, SQLite locks the entire database file during writes. WAL mode changes this by appending writes to a separate log file while readers continue reading the main database unimpeded:

```sql
PRAGMA journal_mode = WAL;
PRAGMA busy_timeout = 5000;
PRAGMA synchronous = NORMAL;
```

With WAL mode enabled, SQLite handles multiple concurrent readers and sequential writes with sub-millisecond response times. For applications serving hundreds of thousands of requests per month where the read-to-write ratio is 95:5, SQLite isn't just adequate—it is often faster and far simpler to operate than an external database cluster.
""",
    },
    {
        "title": "A Photographer's Eye in the Browser",
        "slug": "a-photographers-eye-in-the-browser",
        "created_at": datetime(2026, 8, 16, 9, 15, tzinfo=timezone.utc),
        "excerpt": "How composition, negative space, and tonal balance translate from the camera viewfinder to CSS.",
        "body": """Before I wrote backend code, I spent years looking through a 35mm viewfinder. When you compose a photograph, you quickly learn that what you choose to exclude is just as important as what you leave inside the frame.

Web interfaces frequently suffer from fear of empty space. Product teams often feel compelled to fill every viewport square with banners, badges, floating widgets, and repetitive callouts. The result is visual noise that tires the eye and obscures the core message.

### Lessons from the Viewfinder

1. **Negative space as structural silence:** In photography, negative space gives the subject room to breathe and directs the viewer's attention. In CSS, generous margins and uncrowded line-heights do the exact same work.
2. **Tonal hierarchy over bright accents:** A great monochrome photograph relies on values—deep blacks, subtle midtones, and crisp highlights. When designing digital layouts, establishing contrast through thoughtful typography and surface values reduces the need for distracting accent colors.
3. **Intentional rhythm:** A sequence of photographs in an exhibition tells a story through pacing and scale variation. Similarly, web pages feel most natural when dense technical details alternate with quiet, reflective passages.

When technology respects visual restraint, the interface gets out of the way, and the work speaks for itself.
""",
    },
    {
        "title": "Content Security Policy Beyond the Basics",
        "slug": "content-security-policy-beyond-the-basics",
        "created_at": datetime(2026, 8, 21, 16, 45, tzinfo=timezone.utc),
        "excerpt": "Hardening HTTP response headers to prevent XSS and unwanted third-party script execution without breaking client workflows.",
        "body": """A robust Content Security Policy (CSP) is one of the most effective defensive layers you can deploy on a modern web application. Yet many teams avoid implementing strict CSPs because configuring them can feel tedious, and misconfigurations can inadvertently break frontend features.

### The Problem with Permissive Policies

Too often, sites ship with a token CSP header that includes `'unsafe-inline'` or wildcards like `*.googleapis.com`:

```http
Content-Security-Policy: default-src 'self' 'unsafe-inline' https:;
```

A policy like that provides very little real security against Cross-Site Scripting (XSS). If an attacker finds an injection point, the browser will happily execute the malicious inline script or load external payloads from any HTTPS domain.

### A Hardened Baseline

On this portfolio, I use strict origin isolation. Scripts and styles must originate exclusively from our domain or explicitly defined origins:

```python
CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ["'self'"],
        "script-src": ["'self'"],
        "style-src": ["'self'"],
        "font-src": ["'self'"],
        "img-src": ["'self'", "data:"],
        "frame-ancestors": ["'none'"],
        "base-uri": ["'self'"],
        "form-action": ["'self'"],
    }
}
```

By self-hosting all fonts and styles and eliminating inline scripts, you eliminate entire classes of injection vulnerabilities at the HTTP boundary. Security doesn't have to be complex—it just has to be consistent.
""",
    },
    {
        "title": "Why I Handcraft CSS Without Heavy Frameworks",
        "slug": "why-i-handcraft-css-without-heavy-frameworks",
        "created_at": datetime(2026, 8, 26, 11, 20, tzinfo=timezone.utc),
        "excerpt": "The deliberate choice to write semantic, bespoke stylesheets instead of shipping mega-framework utility classes.",
        "body": """Utility-first CSS frameworks like Tailwind have gained massive popularity, and for rapid prototyping in large teams, their utility is obvious. But for projects where distinct brand identity, minimal bundle size, and long-term maintainability matter, hand-crafted CSS remains my preferred choice.

### What Modern CSS Gives Us

Modern CSS is completely different from the CSS of ten years ago. Today, vanilla CSS natively provides:

- **CSS Custom Properties (Variables):** Dynamic theming, spacing scales, and color palettes that update without compile steps.
- **CSS Grid and Flexbox:** Powerful layout primitives that handle asymmetric, responsive compositions in a dozen lines.
- **`clamp()` and fluid typography:** Fluid scales that transition smoothly from mobile viewports to desktop displays without media query bloat.

### The Cost of Abstractions

When you build with utility frameworks, your HTML markup becomes tightly coupled to presentation classes. A simple button might carry twenty utility classes that must be duplicated across templates or abstracted into component layers.

With hand-written semantic CSS, the HTML describes the document structure, while the stylesheet governs the aesthetics:

```css
.project-card {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr);
  gap: clamp(1.5rem, 4vw, 3rem);
  padding: 2.5rem 0;
  border-top: 1px solid var(--border-subtle);
}
```

The resulting stylesheet is compact, cacheable, and directly understandable by anyone inspecting the code a decade from now.
""",
    },
    {
        "title": "Local-First Architecture with Vue 3 and Capacitor",
        "slug": "local-first-architecture-with-vue-3-and-capacitor",
        "created_at": datetime(2026, 8, 30, 13, 0, tzinfo=timezone.utc),
        "excerpt": "Architectural patterns for building mobile apps where user data stays on their device by default.",
        "body": """When building [Michi](/projects/michi/), my goal was to create a reflective daily practice app that respected user privacy completely. In a world where mental wellness apps routinely monetize personal journals and sync private thoughts to cloud databases, keeping user reflections strictly local was a non-negotiable requirement.

### The Local-First Pattern

Local-first software treats the user's device as the primary source of truth. The application doesn't require an internet connection to function, doesn't mandate account creation, and never sends private user entries to a remote server.

### Dual-Target Persistence

To keep the development workflow rapid while supporting both web previews and native Android distribution, I designed an adaptive persistence layer:

```javascript
export async function getStorageDriver() {
  if (Capacitor.isNativePlatform()) {
    return new SQLiteDriver('michi_vault.db');
  }
  return new LocalStorageDriver('michi_vault');
}
```

On Android, Capacitor bridges writes directly into an encrypted SQLite database on the handset filesystem. In the browser, it seamlessly falls back to reactive storage.

### The Engineering Benefit

Eliminating server synchronization drastically simplified the architecture. There were no WebSocket connections to maintain, no distributed conflict resolution algorithms to debug, and zero server hosting costs for user data storage. True privacy and engineering simplicity worked hand in hand.
""",
    },
    {
        "title": "The Overhead of Premature Microservices",
        "slug": "the-overhead-of-premature-microservices",
        "created_at": datetime(2026, 9, 4, 15, 45, tzinfo=timezone.utc),
        "excerpt": "Why modular monoliths remain the most honest, cost-effective architecture for independent engineers and growing products.",
        "body": """Microservices solve an organizational problem: how to allow hundreds of engineers at a large company to deploy code without stepping on each other's toes. Unfortunately, the tech industry frequently confuses organizational scaling patterns with technical best practices.

When small teams or independent engineers adopt microservices prematurely, they don't get the benefits of scale—they simply inherit the distributed systems tax:

1. **Network latency:** In-process function calls (nanoseconds) turn into HTTP or gRPC requests across networks (milliseconds).
2. **Partial failure modes:** What was once an atomic database transaction now requires two-phase commits, saga orchestrators, and complex retry queues.
3. **Operational overhead:** Instead of monitoring one well-instrumented application, you now have to manage container registries, service meshes, distributed tracing, and fragmented log streams.

### The Modular Monolith Alternative

A modular monolith written in a framework like Django or Go provides clear domain boundaries through packages or apps, without the distributed complexity:

- Database transactions are atomic.
- Refactoring across modules is checked by compilers or unit tests in seconds.
- Deployment is a single Docker image or binary that starts up reliably every time.

Build the monolith first. If a specific component truly demands independent scaling or separate hardware later, extracting it is straightforward because the domain boundaries are already well defined.
""",
    },
    {
        "title": "Automating Responsive WebP Derivatives on Upload",
        "slug": "automating-responsive-webp-derivatives-on-upload",
        "created_at": datetime(2026, 9, 9, 10, 10, tzinfo=timezone.utc),
        "excerpt": "Building an image pipeline in Python Pillow that delivers optimized multi-resolution WebP variants on save.",
        "body": """Images account for the vast majority of bytes transferred on modern websites. Delivering an unoptimized 4MB JPEG to a mobile phone on a cellular connection degrades load times, drains battery life, and hurts search rankings.

While third-party image CDNs exist, they introduce external billing dependencies, DNS lookups, and potential downtime vectors. For this portfolio, I built an automated, self-hosted responsive pipeline directly into the Django ORM.

### The Pipeline Workflow

Whenever an image is uploaded through Django admin:

1. **Content Hashing:** The file's binary content is hashed with SHA-256 to generate an immutable, collision-resistant identifier.
2. **Derivative Generation:** Using Pillow and `ImageOps.exif_transpose`, the image is resized to standard responsive widths (480px, 960px, 1600px) and encoded as WebP at 82% quality.
3. **Metadata Storage:** The resulting file paths and dimensions are saved into a JSONField on the model.

```python
def generate_image_variants(instance):
    # Generates 480w, 960w, and 1600w WebP derivatives
    # Stores results in instance.image_variants
```

### The Output in HTML

The template renders a native `srcset` with matching `sizes` attributes:

```html
<img src="/media/variants/project/abc/960.webp"
     srcset="/media/variants/project/abc/480.webp 480w,
             /media/variants/project/abc/960.webp 960w,
             /media/variants/project/abc/1600.webp 1600w"
     sizes="(max-width: 820px) 100vw, 1200px"
     alt="Project preview" loading="lazy">
```

Browsers automatically select the smallest image that satisfies their display density. Fast, lightweight, and completely self-contained.
""",
    },
    {
        "title": "Rate Limiting and Brute-Force Defense with Django-Axes",
        "slug": "rate-limiting-and-brute-force-defense-with-django-axes",
        "created_at": datetime(2026, 9, 14, 18, 30, tzinfo=timezone.utc),
        "excerpt": "Shielding authentication endpoints and public contact forms from automated credential stuffing.",
        "body": """Every public-facing website on the internet is continuously probed by automated scrapers, vulnerability scanners, and credential-stuffing bots. If your administration panel or login route is left unprotected, botnets will test thousands of common passwords against your credentials every hour.

### Defending the Admin Gateway

Security in depth starts with reducing exposure:

1. **Obscure URL prefixes:** Moving the administration panel away from `/admin/` to a custom secret route prevents generic bot sweeps.
2. **Lockout mechanics with Django-Axes:** Tracking failed authentication attempts by client IP and username.
3. **Cool-off windows:** Temporarily locking out an IP address after consecutive failures before allowing further attempts.

```python
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 1  # 1 hour lockout
AXES_LOCKOUT_CALLABLE = 'security.views.lockout_response'
AXES_IP_GETTER = 'security.utils.get_client_ip'
```

### Trusting Reverse Proxy Headers Carefully

When running behind Nginx or Docker Compose, requests arrive with the reverse proxy's internal IP unless you carefully parse the `X-Forwarded-For` header. Misconfiguring this can lead to locking out your own proxy server or allowing attackers to spoof client IPs.

By ensuring your upstream proxy strips unauthorized headers and setting `NUM_PROXIES = 1` in Axes, client IPs are resolved accurately, ensuring that bad actors are stopped without affecting legitimate visitors.
""",
    },
    {
        "title": "Zero-Server-RAM Clients: The Power of Pre-Compiled Bundles",
        "slug": "zero-server-ram-clients-the-power-of-pre-compiled-bundles",
        "created_at": datetime(2026, 9, 19, 12, 0, tzinfo=timezone.utc),
        "excerpt": "How offloading UI rendering and state to client devices keeps lightweight cloud servers responsive and affordable.",
        "body": """Modern server-side rendering (SSR) frameworks can be wonderful for SEO, but they come with a hidden operational cost: heavy server memory consumption. Running Node.js SSR runtimes often requires 500MB to 1GB of server RAM just to render HTML strings for incoming visitors.

When designing [CommunityWeave](/projects/communityweave/), I explored an alternative: the **Zero-Server-RAM Client**.

### Compiling to the Edge of the Device

Instead of rendering dynamic UI trees on the server, the frontend compiles into a completely static, pre-optimized client bundle (Vue 3 + Vite). When packaged via Capacitor into an Android APK or loaded as an installable PWA:

- All DOM operations, animation states, and interactive map components execute inside the user's phone RAM.
- The server doesn't execute JavaScript runtimes or maintain session render buffers.
- The backend remains a lean Django REST API that serves compressed JSON payloads.

### The Operational Impact

A modest $5/month cloud VPS with 1GB of RAM can easily handle hundreds of concurrent mobile app users when all the server needs to do is query SQLite and return JSON responses. By respecting the computing power already present in the user's pocket, you build faster applications and keep infrastructure overhead negligible.
""",
    },
    {
        "title": "State Machines Over Loose Boolean Flags",
        "slug": "state-machines-over-loose-boolean-flags",
        "created_at": datetime(2026, 9, 24, 16, 15, tzinfo=timezone.utc),
        "excerpt": "Replacing scattered boolean conditions with explicit state transitions for bug-free application logic.",
        "body": """One of the most common anti-patterns in backend development is the accumulation of boolean flags on database models:

```python
# The anti-pattern:
class Order(models.Model):
    is_placed = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)
    is_shipped = models.BooleanField(default=False)
    is_cancelled = models.BooleanField(default=False)
    is_refunded = models.BooleanField(default=False)
```

With five booleans, your entity can technically exist in $2^5 = 32$ different states—many of which are nonsensical or contradictory (e.g. `is_placed=False`, `is_shipped=True`, `is_refunded=True`).

### Modeling with Explicit States

A finite state machine simplifies this by defining valid states and explicit transitions:

```python
class OrderState(models.TextChoices):
    DRAFT = "draft", "Draft"
    PENDING = "pending", "Pending Payment"
    PAID = "paid", "Paid"
    SHIPPED = "shipped", "Shipped"
    CANCELLED = "cancelled", "Cancelled"

class Order(models.Model):
    state = models.CharField(
        max_length=20,
        choices=OrderState.choices,
        default=OrderState.DRAFT
    )
```

### Guarding Transitions

Instead of scattering boolean updates across views, encapsulate transitions in model methods that enforce validation:

```python
def mark_paid(self):
    if self.state != OrderState.PENDING:
        raise ValueError(f"Cannot transition to PAID from {self.state}")
    self.state = OrderState.PAID
    self.save(update_fields=["state"])
```

When invalid states are made unrepresentable by design, entire classes of edge-case bugs simply cease to exist.
""",
    },
    {
        "title": "The Ethics of Minimal Telemetry",
        "slug": "the-ethics-of-minimal-telemetry",
        "created_at": datetime(2026, 9, 28, 14, 50, tzinfo=timezone.utc),
        "excerpt": "Why choosing not to track users is both an engineering benefit and a fundamental respect for user agency.",
        "body": """Open almost any commercial website today and inspect the network tab. You will typically find dozens of tracking scripts, pixel beacons, session recorders, and analytics vendors silently logging your cursor movements, viewport dimensions, battery levels, and referrer trails.

This pervasive surveillance is usually justified under the banner of \"optimizing user experience.\" In reality, it reflects an unexamined assumption that more data is always better.

### What Telemetry Actually Costs

1. **User Trust:** Visitors are increasingly tech-savvy. They notice intrusive consent banners, third-party redirects, and bloated page sizes.
2. **Performance Degradation:** Third-party tracking scripts block the main thread, delay Largest Contentful Paint (LCP), and increase total page weight.
3. **Legal and Operational Burden:** Managing GDPR, CCPA, and data processing agreements adds ongoing legal complexity for little tangible return.

### The Deliberate Choice: Zero Surveillance

On this website and in the products I build for clients, I intentionally avoid third-party analytics scripts. Server-side log aggregates (like Gunicorn access logs) provide all the necessary operational signals:

- What pages are returning 404 or 500 errors?
- What are the overall request volumes?
- Which static assets are consuming bandwidth?

You can build exceptional, high-converting digital products without tracking your users' every click. Respecting privacy is not a limitation—it is a feature.
""",
    },
    {
        "title": "Bayanihan and Neighborhood Tech: Building CommunityWeave",
        "slug": "bayanihan-and-neighborhood-tech-building-communityweave",
        "created_at": datetime(2026, 10, 2, 11, 40, tzinfo=timezone.utc),
        "excerpt": "Notes on designing a hyperlocal mutual-aid sharing platform tailored for Philippine communities.",
        "body": """In Philippine culture, *Bayanihan* refers to the spirit of communal unity and cooperation—traditionally exemplified by neighbors literally coming together to lift and move a family's nipa hut to a new location.

In modern cities like Caloocan, Quezon City, and Manila, that spirit still thrives, but people often lack a dedicated digital channel to practice it. General social media groups are overwhelmed by commercial ads, algorithmic feeds, and irrelevant noise.

### Designing [CommunityWeave](/projects/communityweave/)

When building CommunityWeave, the focus was to translate that communal impulse into a digital utility:

- **Hyperlocal scoping:** Posts are categorized by specific neighborhoods and barangays so assistance remains physically practical.
- **Two simple verbs: Requests and Offers:** Whether you need to borrow a ladder for an afternoon or have extra mangoes from your backyard tree to share, interactions are structured around clear reciprocal actions.
- **Direct, private communication:** Once an offer or request is accepted, neighbors connect through direct messaging without exposing personal phone numbers or public social profiles.

### Keeping the Experience Humane

Software designed for communities shouldn't try to maximize daily active screen time. The goal is to facilitate an offline connection as quickly as possible and then get out of the way so people can help one another in real life.
""",
    },
    {
        "title": "Cache Invalidation and WhiteNoise Manifests",
        "slug": "cache-invalidation-and-whitenoise-manifests",
        "created_at": datetime(2026, 10, 6, 17, 10, tzinfo=timezone.utc),
        "excerpt": "Achieving zero-downtime, fingerprinted static asset caching without third-party CDN complexity.",
        "body": """Serving static assets in production sounds deceptively simple until you deploy your first CSS update and realize your users' browsers are still rendering old styles from local cache.

The traditional workaround was query string busting (e.g. `style.css?v=2`). However, query strings are unreliable: many intermediate proxies and CDNs refuse to cache URLs with query parameters altogether.

### Enter Content-Hash Manifests

WhiteNoise's `CompressedManifestStaticFilesStorage` provides a robust, zero-configuration solution built directly into Python:

```python
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
WHITENOISE_MAX_AGE = 31_536_000  # 1 year in seconds
```

When `collectstatic` runs during container build:

1. WhiteNoise computes an MD5 hash of each static file's binary contents.
2. It generates a fingerprinted filename, such as `style.0bc7e7298d0c.css`.
3. It pre-compresses both Gzip and Brotli representations alongside the file.
4. Django's `{% static %}` template tag automatically renders the fingerprinted path.

### The 1-Year Immutable Header

Because the filename changes whenever the content changes, we can safely instruct browsers to cache static assets for an entire year with the `immutable` directive:

```http
Cache-Control: public, max-age=31536000, immutable
```

Repeat visits load instantly from disk cache, zero CDN configuration is required, and cache invalidation is 100% reliable on every deploy.
""",
    },
    {
        "title": "Why Boring Architecture Lets Small Teams Ship Faster",
        "slug": "why-boring-architecture-lets-small-teams-ship-faster",
        "created_at": datetime(2026, 10, 10, 13, 25, tzinfo=timezone.utc),
        "excerpt": "Choosing proven, predictable technologies allows independent developers to focus on customer problems rather than infrastructure churn.",
        "body": """In 2015, Dan McKinley wrote a classic essay titled *Choose Boring Technology*. More than a decade later, that advice remains the single best architectural heuristic for independent engineers.

Every technology in your stack has an operational cost. When you choose cutting-edge, experimental tools, you spend valuable cognitive cycles learning unwritten edge cases, diagnosing library bugs, and reading incomplete documentation.

### The Compound Leverage of Boring Tech

When I build client projects or personal products, I routinely reach for tools that have been proven over twenty years:

- **Python & Django:** Batteries included, robust ORM, battle-tested security defaults, and clear documentation.
- **SQLite:** Fast, reliable, single-file persistence with zero server management.
- **Docker Compose:** Portable, reproducible deployment environments across any Linux virtual server.
- **Vanilla CSS & Semantic HTML:** Rendered instantly by any web browser without compilation overhead.

### Innovation Tokens Where They Count

You only have a few \"innovation tokens\" to spend on any given project. If you spend those tokens on your database driver, your build bundler, and your deployment orchestrator, you have none left for the actual product logic, the user interface, and the editorial design.

Choose boring infrastructure. Spend your creativity on the user experience.
""",
    },
    {
        "title": "The Discipline of Deliberate Simplicity",
        "slug": "the-discipline-of-deliberate-simplicity",
        "created_at": datetime(2026, 10, 14, 15, 0, tzinfo=timezone.utc),
        "excerpt": "The hardest engineering skill isn't knowing what to add, but having the restraint to leave things out.",
        "body": """In software engineering, complexity accumulates almost imperceptibly. A client asks for a small toggle. An engineer thinks of an edge case that might occur once a year and adds a configuration flag. A designer adds another modal layer to capture secondary feedback.

Before long, an application that started as a clear, focused tool becomes a maze of conditional branches, settings panels, and maintenance headaches.

### Simplicity as an Active Practice

Simplicity is rarely an accident; it is the result of continuous, disciplined subtraction:

- **Saying no to features that dilute focus:** A tool that does two things exceptionally well is infinitely more valuable than one that does ten things poorly.
- **Writing code that can be deleted:** Small, self-contained functions and decoupled modules are easy to replace or delete when requirements change.
- **Valuing understandability over cleverness:** Code is read twenty times more often than it is written. If a junior developer cannot understand your abstraction in five minutes, it is probably too clever.

### Built with Purpose. Made with Care.

When you look at enduring physical objects—a well-made mechanical watch, a Leica rangefinder, a solid hardwood chair—their beauty comes from the harmony of essential parts working together without superfluous ornament.

Software should aspire to the same standard. Build only what is needed, build it thoughtfully, and give it the care it deserves.
""",
    },
]


def add_posts(apps, schema_editor):
    Post = apps.get_model("core", "Post")
    for item in POSTS:
        post, created = Post.objects.get_or_create(
            slug=item["slug"],
            defaults={
                "title": item["title"],
                "excerpt": item["excerpt"],
                "body": item["body"],
                "published": True,
            },
        )
        if not created:
            post.title = item["title"]
            post.excerpt = item["excerpt"]
            post.body = item["body"]
            post.published = True
            post.save()
        # Set exact created_at timestamp
        Post.objects.filter(pk=post.pk).update(created_at=item["created_at"])


def remove_posts(apps, schema_editor):
    Post = apps.get_model("core", "Post")
    slugs = [item["slug"] for item in POSTS]
    Post.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0010_populate_communityweave_case_study"),
    ]

    operations = [
        migrations.RunPython(add_posts, remove_posts),
    ]
