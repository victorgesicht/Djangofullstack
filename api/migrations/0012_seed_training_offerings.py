from django.db import migrations

OFFERINGS = [
    {
        "slug": "web-app-enumeration",
        "title": "Web App Enumeration",
        "kind": "COURSE",
        "track": "WEB_ENUM",
        "level": "OPS",
        "summary": "Map the app before you touch it: content discovery, auth flows, hidden parameters and the API surface behind the UI.",
        "details": (
            "- Content and vhost discovery against WAF-protected targets\n"
            "- Auth and session mapping: cookies, JWT, OAuth flows\n"
            "- Parameter mining and hidden endpoint discovery\n"
            "- Turning Burp/ffuf output into a test plan"
        ),
        "hours": 4,
        "hourly_rate_kes": 2000,
        "sort_order": 10,
    },
    {
        "slug": "active-directory",
        "title": "Active Directory Attack Paths",
        "kind": "COURSE",
        "track": "AD",
        "level": "ADV",
        "summary": "Enumerate, graph and attack an AD estate without breaking it: Kerberos, ACLs, delegation and lateral movement.",
        "details": (
            "- BloodHound collection and attack-path reading\n"
            "- Kerberoasting, AS-REP roasting and safe password spraying\n"
            "- ACL/ACE abuse and delegation paths\n"
            "- Lateral movement, loot hygiene and cleanup"
        ),
        "hours": 8,
        "hourly_rate_kes": 2000,
        "sort_order": 20,
    },
    {
        "slug": "osint",
        "title": "OSINT Target Mapping",
        "kind": "COURSE",
        "track": "OSINT",
        "level": "FND",
        "summary": "Turn a domain, handle or leak into a defensible target map: infrastructure, identities and exposure with source hygiene.",
        "details": (
            "- Passive infra mapping: DNS, certificates, ASN, favicon pivots\n"
            "- Identity and credential-leak discovery\n"
            "- Evidence handling, citation and false-positive control\n"
            "- OPSEC for the researcher"
        ),
        "hours": 3,
        "hourly_rate_kes": 2000,
        "sort_order": 30,
    },
    {
        "slug": "initial-access",
        "title": "Initial Access Tradecraft",
        "kind": "COURSE",
        "track": "INITIAL_ACCESS",
        "level": "OPS",
        "summary": "Get the first shell legally: exposed services, valid accounts, phishing infrastructure and supply-chain edges.",
        "details": (
            "- External service triage and exploit validation\n"
            "- Password/identity attacks and MFA realities\n"
            "- Phishing and payload delivery in an authorized campaign\n"
            "- Choosing the quietest path in"
        ),
        "hours": 6,
        "hourly_rate_kes": 2000,
        "sort_order": 40,
    },
    {
        "slug": "backdoors-persistence",
        "title": "Backdoors & Persistence",
        "kind": "COURSE",
        "track": "BACKDOORS",
        "level": "ADV",
        "summary": "Persistence that survives reboots and reviews: beacons, services, scheduled tasks and the tradecraft to hide them.",
        "details": (
            "- Windows and Linux persistence primitives\n"
            "- Beacon design, jitter and egress over HTTP(S)/DNS\n"
            "- Detection trade-offs and cleanup\n"
            "- Documenting persistence for the report"
        ),
        "hours": 5,
        "hourly_rate_kes": 2000,
        "sort_order": 50,
    },
    {
        "slug": "web-programming-apis",
        "title": "Web Programming & APIs",
        "kind": "COURSE",
        "track": "WEB_APIS",
        "level": "OPS",
        "summary": "Break and build APIs: authz flaws, mass assignment, rate-limit gaps and secure-by-default implementation.",
        "details": (
            "- REST/GraphQL enumeration and schema abuse\n"
            "- Broken object-level authorization and mass assignment\n"
            "- Rate-limit, token and session weaknesses\n"
            "- Fixing what you find in code"
        ),
        "hours": 6,
        "hourly_rate_kes": 2000,
        "sort_order": 60,
    },
    {
        "slug": "forensics",
        "title": "Forensics & Incident Triage",
        "kind": "COURSE",
        "track": "FORENSICS",
        "level": "OPS",
        "summary": "Answer 'what happened' under pressure: memory, disk and log triage with a chain of custody that holds up.",
        "details": (
            "- Volatile data collection and memory triage\n"
            "- Disk artefacts: MFT, registry, browser, event logs\n"
            "- Timeline building and lateral-movement evidence\n"
            "- Evidence handling and reporting"
        ),
        "hours": 6,
        "hourly_rate_kes": 2000,
        "sort_order": 70,
    },
    {
        "slug": "ad-attack-path-review",
        "title": "AD Attack-Path Review",
        "kind": "CONSULT",
        "track": "",
        "level": "OPS",
        "summary": "Bring your AD graph. We read the paths together and pick the three that actually matter.",
        "details": (
            "- 60-minute working session\n"
            "- BloodHound export or screenshots\n"
            "- Prioritized attack paths and fixes"
        ),
        "hours": 1,
        "hourly_rate_kes": 2000,
        "sort_order": 80,
    },
    {
        "slug": "dfir-triage-sprint",
        "title": "DFIR Triage Sprint",
        "kind": "CONSULT",
        "track": "",
        "level": "OPS",
        "summary": "A focused incident triage sprint: what happened, what is still live, and what to preserve before it disappears.",
        "details": (
            "- 2-hour live triage\n"
            "- Volatile data and log review\n"
            "- Immediate containment checklist"
        ),
        "hours": 2,
        "hourly_rate_kes": 2000,
        "sort_order": 90,
    },
]

SLUGS = [row["slug"] for row in OFFERINGS]


def seed(apps, schema_editor):
    Offering = apps.get_model("api", "TrainingOffering")
    for row in OFFERINGS:
        defaults = {key: value for key, value in row.items() if key != "slug"}
        Offering.objects.get_or_create(slug=row["slug"], defaults=defaults)


def unseed(apps, schema_editor):
    Offering = apps.get_model("api", "TrainingOffering")
    Offering.objects.filter(slug__in=SLUGS).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0011_training_models"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
