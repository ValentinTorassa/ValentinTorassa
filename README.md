<!-- Text between brain:<section>:start and brain:<section>:end markers is generated from the Brain by scripts/sync_from_brain.py. Edit it there, not here. -->
<h1 align="center">Valentín Torassa Colombero</h1>

<p align="center">
  <strong>Cybersecurity & Backend Engineer · Cloud Security · Go · Linux · Open Source</strong>
</p>

<p align="center">
  Building secure systems for AI agents and teaching practical technology through VT Security.
</p>

I am a Cybersecurity and Backend Engineer based in Rosario, Argentina. I build and secure cloud-backed systems, with a particular interest in identity, permissions, observability, and the Linux and networking layers underneath modern abstractions.

Alongside my professional work, I create open-source software and practical Spanish-language education through [VT Security](https://www.youtube.com/@vtcibersecurity).

I write long-form technical notes at **[vtsecurity.com.ar](https://vtsecurity.com.ar)** - Linux, Git and security, with the diagrams and the exact commands I actually use. I care about work that leaves reviewable evidence: running code, labs, documentation, tests, research, and talks.

## Current role & focus

<!-- brain:role:start -->
### Teramot - Cybersecurity Engineer & Software Architect

*Nov. 2025-present*

- Work across technical cybersecurity, AWS architecture and security, compliance, and backend engineering.
- Lead a team of four across security and backend work.
- Build Go backend systems and secure AI-agent integrations for controlled access to enterprise data.
- Translate SOC 2 and ISO/IEC 27001 requirements into verifiable technical implementations and evidence.
- Focus on OAuth/OIDC, permissions, sensitive-data boundaries, observability, and operational reliability.

**Current focus:** AI-agent authorization, MCP security, detection engineering, cloud identity, and low-level Linux fundamentals.

Previously, I worked as a Cybersecurity & Compliance Analyst at Teramot, a Cybersecurity Analyst at Consulting IT, and a Teaching Assistant for Computer Architecture II at Universidad Abierta Interamericana.
<!-- brain:role:end -->

## Projects & open source

<!-- brain:projects:start -->
- **[Open Security Labs](https://github.com/ValentinTorassa/Open-Security-Labs)** - My flagship open-source education project: practical Spanish-language labs covering Linux, networking, backend engineering, cloud, DevSecOps, AI agents, and cybersecurity. **[Explore the platform →](https://securitylabs.valentorassa.com/)**
- **[VT-SecretShare](https://github.com/ValentinTorassa/VT-SecretShare)** - Self-hosted, one-time secret sharing with browser-side AES-256-GCM encryption, a Go API, and atomic deletion through Redis GETDEL.
- **[VT-Agent-Firewall](https://github.com/ValentinTorassa/VT-Agent-Firewall)** - A local security gateway between an AI agent and its tools (filesystem, shell, network, MCP): default-deny policy engine, human approval, and an append-only audit log, tested against indirect prompt injection. It is a security lab, not a production sandbox: it enforces policy around the tool call, not at the operating-system boundary.
- **[pluma](https://github.com/ValentinTorassa/pluma)** - The open-source blog platform behind vtsecurity.com.ar and yaninacolombero.com: per-tenant contracts, isolated deployments, content sanitization, and per-instance validation. Tenant selection happens at build time, so each site ships as its own deployment.
- **[VT-Lens](https://github.com/ValentinTorassa/VT-Lens)** - A native Rust GUI for understanding local process and network activity, turning a selected slice of evidence into an LLM-ready prompt or Markdown export. It reads `/proc` without root and is an educational instrument, not an EDR or a packet sniffer.
- **[VT-Ragnaros](https://github.com/ValentinTorassa/VT-Ragnaros)** - A reverse-engineered, from-scratch Linux driver and daemon for the Ragnaros USB control deck: libusb transport, 10 LCD keys, 4 rotary knobs, a touch strip, and YAML profiles. It runs entirely in user space; there is no kernel module.
- **[VT-Security-Fixes](https://github.com/ValentinTorassa/VT-Security-Fixes)** - DEP-3-formatted security patches for open-source packages that miss standard distribution updates, currently focused on Ubuntu universe CVEs.
- **[VT-Terminal-Project](https://github.com/ValentinTorassa/VT-Terminal-Project)** - A reproducible macOS and Linux terminal environment with Zsh, Ghostty, modern CLI tools, searchable cheatsheets, and AI-assisted workflows.
- **[VT-IDE-Project](https://github.com/ValentinTorassa/VT-IDE-Project)** - An AI-native Zed setup with MCP integrations, inline assistance, and structured Git review, conflict-resolution, and diff workflows.
<!-- brain:projects:end -->

### Contribution highlight

My merged Podman contribution, **[Add <code>--retry</code> support to <code>manifest push</code> - PR #28637](https://github.com/podman-container-tools/podman/pull/28637)**, added <code>--retry</code> and <code>--retry-delay</code> across the CLI, local and remote clients, REST API, manpages, Swagger documentation, and end-to-end tests.

It is a small feature with a production lesson behind it: reliable infrastructure requires explicit behavior for temporary network and registry failures.

## Technical toolkit

These are the technologies I use across secure backend systems, cloud infrastructure, identity, observability, and systems engineering.

**Backend and data**

<p>
  <img src="https://img.shields.io/badge/Go-00ADD8?style=for-the-badge&logo=go&logoColor=white" alt="Go" />
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Rust-000000?style=for-the-badge&logo=rust&logoColor=white" alt="Rust" />
  <img src="https://img.shields.io/badge/C%23-512BD4?style=for-the-badge&logo=csharp&logoColor=white" alt="C Sharp" />
  <img src="https://img.shields.io/badge/.NET-512BD4?style=for-the-badge&logo=dotnet&logoColor=white" alt=".NET" />
  <img src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript" />
  <img src="https://img.shields.io/badge/React-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React" />
  <img src="https://img.shields.io/badge/REST_APIs-02569B?style=for-the-badge&logo=fastapi&logoColor=white" alt="REST APIs" />
  <img src="https://img.shields.io/badge/OpenAPI-6BA539?style=for-the-badge&logo=openapiinitiative&logoColor=white" alt="OpenAPI" />
  <img src="https://img.shields.io/badge/NATS-27AAE1?style=for-the-badge&logo=natsdotio&logoColor=white" alt="NATS" />
  <img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
  <img src="https://img.shields.io/badge/SQL_Server-CC2927?style=for-the-badge&logo=microsoftsqlserver&logoColor=white" alt="SQL Server" />
</p>

**Cloud and operations**

<p>
  <img src="https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazonwebservices&logoColor=white" alt="AWS" />
  <img src="https://img.shields.io/badge/ECS_%2F_Fargate-FF9900?style=for-the-badge&logo=amazonwebservices&logoColor=white" alt="AWS ECS and Fargate" />
  <img src="https://img.shields.io/badge/AWS_IAM-232F3E?style=for-the-badge&logo=amazonwebservices&logoColor=white" alt="AWS IAM" />
  <img src="https://img.shields.io/badge/CloudTrail-FF9900?style=for-the-badge&logo=amazonwebservices&logoColor=white" alt="AWS CloudTrail" />
  <img src="https://img.shields.io/badge/GuardDuty-FF9900?style=for-the-badge&logo=amazonwebservices&logoColor=white" alt="AWS GuardDuty" />
  <img src="https://img.shields.io/badge/Terraform-844FBA?style=for-the-badge&logo=terraform&logoColor=white" alt="Terraform" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
  <img src="https://img.shields.io/badge/Podman-892CA0?style=for-the-badge&logo=podman&logoColor=white" alt="Podman" />
  <img src="https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white" alt="GitHub Actions" />
  <img src="https://img.shields.io/badge/OpenTelemetry-000000?style=for-the-badge&logo=opentelemetry&logoColor=white" alt="OpenTelemetry" />
</p>

**Security and compliance**

<p>
  <img src="https://img.shields.io/badge/OAuth_2.1-EB5424?style=for-the-badge&logo=auth0&logoColor=white" alt="OAuth 2.1" />
  <img src="https://img.shields.io/badge/OpenID_Connect-F78C40?style=for-the-badge&logo=openid&logoColor=white" alt="OpenID Connect" />
  <img src="https://img.shields.io/badge/JWT_%2F_JWKS-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white" alt="JWT and JWKS" />
  <img src="https://img.shields.io/badge/Secrets_Handling-6F42C1?style=for-the-badge&logo=1password&logoColor=white" alt="Secrets handling" />
  <img src="https://img.shields.io/badge/SOC_2-6F42C1?style=for-the-badge" alt="SOC 2" />
  <img src="https://img.shields.io/badge/ISO%2FIEC_27001-0052CC?style=for-the-badge" alt="ISO IEC 27001" />
</p>

**Linux, containers, and networking**

<p>
  <img src="https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black" alt="Linux" />
  <img src="https://img.shields.io/badge/Debian-A81D33?style=for-the-badge&logo=debian&logoColor=white" alt="Debian" />
  <img src="https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white" alt="Ubuntu" />
  <img src="https://img.shields.io/badge/Bash-4EAA25?style=for-the-badge&logo=gnubash&logoColor=white" alt="Bash" />
  <img src="https://img.shields.io/badge/systemd-000000?style=for-the-badge&logo=linux&logoColor=white" alt="systemd" />
  <img src="https://img.shields.io/badge/WireGuard-88171A?style=for-the-badge&logo=wireguard&logoColor=white" alt="WireGuard" />
  <img src="https://img.shields.io/badge/MikroTik-293239?style=for-the-badge&logo=mikrotik&logoColor=white" alt="MikroTik" />
  <img src="https://img.shields.io/badge/TCP%2FIP-1F6FEB?style=for-the-badge" alt="TCP IP networking" />
  <img src="https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white" alt="Git" />
  <img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub" />
</p>

## Education & certifications

<!-- brain:education:start -->
- **Information Systems Engineering**, Universidad Abierta Interamericana - final year, expected Dec. 2026
- **Information Systems Analyst**, Universidad Abierta Interamericana - completed Dec. 2024, GPA 9.25/10
- **Teaching module for university teaching assistants**, Universidad Abierta Interamericana - module certificate, 2026
- **CompTIA Security+ (SY0-701)** - issued Feb. 2026, valid through Feb. 2029
- **AWS Certified Cloud Practitioner (CLF-C02)** - issued Jul. 2025, valid through Jul. 2028
- **Linux Foundation Certified IT Associate (LFCA)** - issued Apr. 2026, valid through Apr. 2028
- **Huawei Certified ICT Associate, Datacom (HCIA-Datacom)**
<!-- brain:education:end -->

## Teaching, speaking & research

[VT Security](https://www.youtube.com/@vtcibersecurity) is my Spanish-language education and community platform for practical cybersecurity, Linux, networking, software engineering, and systems fundamentals. Open Security Labs is its flagship public software project.

<!-- brain:community:start -->
I am an **AWS Community Builder**, in my first year in the programme.
<!-- brain:community:end -->

<!-- brain:talks:start -->
### Upcoming

- **Joven Argentina (FNGA), Rosario, Sep. 28, 2026:** cybersecurity talk and exchange for a programme of young leaders
- **Hacking Day 2026, Paraná, Oct. 2, 2026:** *Firewall para agentes de IA: prompt injection en vivo* (main stage, 45 min)
- **CACIC 2026, UTN FRCU, Concepción del Uruguay, Oct. 5-9, 2026:** author and presenter of two accepted papers, on Podman/FOSS contribution and on Ubuntu universe SRU work
- **Ekoparty 2026, Buenos Aires, Oct. 7-9, 2026:** two talks, *Prompt injection en agentes con tools* at the AI Resilience Hub Village and *GitOps: cuando la fuente de verdad también es el riesgo* at the DevSecOps Space Village
- **JCC XXIV 2026, FCEIA, UNR, Oct. 21-23, 2026:** invited 45-minute talk on systems, Linux, cloud and AI security

### Past talks and research

- **[DebConf26](https://debconf26.debconf.org/talks/75-abstraction-leaks-why-understanding-linux-internals-still-matters/), July 24, 2026:** *Abstraction Leaks: Why Understanding Linux Internals Still Matters*
- **Webinar UAI, Tecnología Informática, Aug. 19, 2026:** *Orquestación, workers y arquitectura moderna: cómo diseñar sistemas que escalan*
- **[Vincular Inteligente 2026](https://vincular-inteligente-2026.vercel.app/), May 22, 2026:** *Seguridad con IA: monitoreo inteligente y respuesta temprana*
- **CyberSecTuc Meetup #3, May 2026:** *La realidad de un Ingeniero en Ciberseguridad*
- **CACIC 2024:** *Expositor Distinguido en Seguridad Informática* for [reverse-shell research](https://sedici.unlp.edu.ar/handle/10915/176994)
- **SACS / 53 JAIIO 2024:** *Mejor Exposición* for [botnet taxonomy research](https://revistas.unlp.edu.ar/JAIIO/article/view/17896)
- **JAIIO 2024:** co-author of [research on monoliths and microservices](https://revistas.unlp.edu.ar/JAIIO/article/view/17984)
- **WICC 2025:** *Dockerización de servidores SCADA: ciberseguridad industrial*
- **WICC 2024:** *Seguridad en redes wifi: estrategias de detección y expulsión de intrusos*
<!-- brain:talks:end -->

<h2 align="center">Find me online</h2>

<p align="center">
  <a href="https://valentorassa.com/"><img src="https://img.shields.io/badge/Portfolio-111827?style=for-the-badge&logo=firefoxbrowser&logoColor=white" alt="Portfolio" /></a>
  <a href="https://vtsecurity.com.ar"><img src="https://img.shields.io/badge/Blog-0B1120?style=for-the-badge&logo=rss&logoColor=FF6600" alt="Blog" /></a>
  <a href="https://github.com/ValentinTorassa"><img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub" /></a>
  <a href="https://www.linkedin.com/in/valetorassa/"><img src="https://custom-icon-badges.demolab.com/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin-white&logoColor=white" alt="LinkedIn" /></a>
  <a href="https://www.youtube.com/@vtcibersecurity"><img src="https://img.shields.io/badge/YouTube_Channel-FF0000?style=for-the-badge&logo=youtube&logoColor=white" alt="YouTube channel" /></a>
  <a href="https://www.tiktok.com/@vtsecurity"><img src="https://img.shields.io/badge/TikTok-25F4EE?style=for-the-badge&logo=tiktok&logoColor=black" alt="TikTok" /></a>
  <a href="https://www.instagram.com/vtsecurity/"><img src="https://img.shields.io/badge/Instagram-E4405F?style=for-the-badge&logo=instagram&logoColor=white" alt="Instagram" /></a>
  <a href="https://x.com/ValenSecurity"><img src="https://img.shields.io/badge/X-000000?style=for-the-badge&logo=x&logoColor=white" alt="X" /></a>
  <a href="https://bsky.app/profile/vtsecurity.bsky.social"><img src="https://img.shields.io/badge/Bluesky-0285FF?style=for-the-badge&logo=bluesky&logoColor=white" alt="Bluesky" /></a>
  <a href="https://www.threads.com/@vt_security_"><img src="https://img.shields.io/badge/Threads-000000?style=for-the-badge&logo=threads&logoColor=white" alt="Threads" /></a>
  <a href="https://discord.com/invite/z6cr5JF6bJ"><img src="https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white" alt="Discord" /></a>
  <a href="mailto:valentin.torassa.colombero@gmail.com"><img src="https://img.shields.io/badge/Email-EA4335?style=for-the-badge&logo=gmail&logoColor=white" alt="Email" /></a>
</p>

<p align="center">
  Rosario, Argentina · UTC-3
</p>
