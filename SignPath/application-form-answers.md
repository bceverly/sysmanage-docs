# SignPath Foundation - Pre-Filled Application Form

## Overview

This document provides pre-filled answers for the SignPath Foundation OSSRequestForm-v4. Review and customize these answers before submitting your application.

**Application URL**: (Check signpath.io for current application page)

## Form Section 1: Basic Information

### Project Name
```
SysManage Agent
```

### Project Short Name / Identifier
```
sysmanage-agent
```

### Project Homepage
```
https://bceverly.github.io/sysmanage-docs/
```

### Project Description (Brief)
```
SysManage Agent is a cross-platform, open-source system monitoring and management tool that provides inventory, configuration management, and compliance monitoring for Linux, Windows, macOS, and BSD systems.
```

### Project Description (Detailed)
```
SysManage Agent is a lightweight, agent-based system management platform designed for modern IT environments. It provides comprehensive system monitoring, configuration management, software inventory, and security compliance checking across heterogeneous infrastructures.

Key Features:
- Cross-platform support (Linux, Windows, macOS, FreeBSD, OpenBSD, NetBSD)
- Agent-based architecture with minimal resource footprint
- Automatic server discovery (no manual configuration required)
- Certificate-based secure authentication
- Software inventory and deployment capabilities
- Security compliance monitoring
- Open source (MIT License) with full transparency

The agent communicates exclusively with self-hosted SysManage servers - no data is transmitted to external third parties. All source code is publicly available and auditable.
```

### License
```
MIT License
```

### License URL
```
https://github.com/bceverly/sysmanage-agent/blob/main/LICENSE
```

### Programming Language(s)
```
Python 3.9+
```

## Form Section 2: Repository Information

### Source Code Repository Type
```
GitHub
```

### Source Code Repository URL
```
https://github.com/bceverly/sysmanage-agent
```

### Number of Contributors
```
[UPDATE with current count]
```

### Number of Commits
```
[UPDATE with current count from: git rev-list --all --count]
```

### Age of Project
```
[UPDATE: Started in YYYY]
[UPDATE: X months/years old]
```

### Development Status
```
Active - Regular commits and releases
```

## Form Section 3: Distribution & Downloads

### Download Page URL
```
https://github.com/bceverly/sysmanage-agent/releases
```

**Alternative/Additional**:
```
https://bceverly.github.io/sysmanage-docs/repo/windows/
```

### Package Formats Available
```
- Windows MSI Installer (x64 and ARM64)
- macOS PKG Installer (Universal Binary)
- Debian/Ubuntu APT Repository (.deb)
- RHEL/CentOS/Fedora/Oracle Linux YUM/DNF Repository (.rpm)
- openSUSE/SLES Zypper Repository
- Source tarball
```

### Distribution Method
```
Primary: GitHub Releases
Secondary: APT/YUM/Zypper package repositories hosted on GitHub Pages
Tertiary: Direct download from documentation site
```

### Total Downloads (All Time)
```
[UPDATE before submission]

Approximate breakdown:
- GitHub Releases: [X] downloads
- APT Repository: [X] installs
- YUM/DNF Repository: [X] installs
- macOS PKG: [X] downloads

Total: [CALCULATE]
```

### Downloads Per Month (Average)
```
[UPDATE based on GitHub Insights and package manager logs]
```

## Form Section 4: Privacy Policy

### Does your software collect and transmit user data?
```
YES - with important caveats (see privacy policy for full details)
```

### What data is collected?
```
System monitoring data including:
- Operating system information and versions
- System resource usage (CPU, memory, disk)
- Installed software inventory
- Network configuration
- Running processes and services
- Configuration compliance status
- Agent operational metrics

Personal data:
- System/computer names (as configured by administrators)
- User account names (as they exist on managed systems)

NOT collected:
- Personal files, documents, or content
- Web browsing history or personal communications
- Financial information or payment data
- Biometric or location data
- Any data beyond system administration scope
```

### Where is data transmitted?
```
EXCLUSIVELY to the user's self-hosted SysManage Server

Important clarifications:
- Data is sent ONLY to the server address YOU configure during installation
- No data is transmitted to the SysManage project developers
- No data is sent to any third-party services
- No telemetry or analytics are sent externally
- The agent does NOT "phone home" to any external service

All data remains within your infrastructure. The SysManage project maintainers have NO access to any data collected by deployed agents.
```

### Privacy Policy URL
```
[UPDATE after publishing]
https://bceverly.github.io/sysmanage-docs/docs/privacy-policy.html
```

**Or**:
```
https://github.com/bceverly/sysmanage-agent/blob/main/PRIVACY.md
```

### How is data used?
```
Collected data is used exclusively for:
1. System monitoring and health tracking
2. Software inventory management
3. Configuration compliance verification
4. Security status monitoring
5. Administrative task execution

Data usage is entirely determined by the system administrator who deployed the agent. The SysManage project itself does not use, access, or analyze any collected data.
```

## Form Section 5: Wikipedia Article

### Wikipedia Article URL (English)
```
[IF CREATED]:
https://en.wikipedia.org/wiki/SysManage

[IF NOT CREATED]:
Not yet available. The project is building notability through active development, user adoption, and community engagement. We plan to pursue Wikipedia article creation once sufficient independent coverage exists.
```

### Why no Wikipedia article?
```
SysManage is a relatively new open source project (started [YEAR]). While we have active development and growing user adoption, we do not yet have the extensive independent media coverage required by Wikipedia's notability guidelines.

We are actively building notability through:
- Conference presentations and talks
- Technical blog posts and tutorials
- Academic and research collaborations
- Growing user base and deployments
- Open source community engagement

We plan to pursue Wikipedia article creation in [TIMEFRAME] once we have accumulated sufficient independent reliable sources as required by Wikipedia guidelines.
```

## Form Section 6: Verification & Trust Evidence

### How can SignPath verify your project is used and trusted?

```
SysManage Agent is actively used and trusted by the open source community, as demonstrated through multiple indicators:

**Repository Metrics:**
- GitHub Repository: https://github.com/bceverly/sysmanage-agent
- Stars: [UPDATE]
- Forks: [UPDATE]
- Contributors: [UPDATE]
- Commits: [UPDATE]
- Active Issues: [UPDATE] open, [UPDATE] closed
- Pull Requests: [UPDATE] merged from external contributors

**Usage Statistics:**
- Total Downloads: [UPDATE] across all platforms
- Package Repository Stats:
  * APT (Ubuntu/Debian): [UPDATE] installations
  * YUM/DNF (RHEL/CentOS/Oracle Linux): [UPDATE] installations
  * macOS PKG: [UPDATE] downloads
  * Windows MSI: [UPDATE] downloads
- Active deployments in [X] known organizations

**Development Activity:**
- Regular commit cadence: [X] commits/month average
- Consistent release schedule: [X] releases in [TIMEFRAME]
- Active maintenance: Issues responded to within [X] hours avg
- Multi-platform CI/CD: Automated testing on Linux, Windows, macOS, BSD

**Code Quality & Security:**
- Clean security scans (Bandit, Dependabot)
- GitHub security alerts: [STATUS]
- Test coverage: [X]%
- Multi-platform compatibility testing
- Open source (MIT) - fully auditable codebase

**Community Engagement:**
- GitHub Discussions: [X] active discussions
- Documentation site: [X] monthly visitors
- Stack Overflow mentions: [X] questions/answers
- Social media engagement: [X] mentions on Twitter, Reddit, LinkedIn

**External References:**
[List any media coverage, blog posts, or articles]
- [Article 1]: [URL]
- [Blog post]: [URL]
- [Tutorial]: [URL]

**OpenHub Profile:**
- [AFTER CREATING]: https://www.openhub.net/p/sysmanage-agent
- [BEFORE]: Profile in process of being created

**Testimonials:**
[Include 2-3 brief user testimonials if available]

"[Quote from user about reliability/usefulness]" - [Name/Role], [Organization if public]

All metrics can be independently verified through public GitHub data, package manager statistics, and web analytics.
```

### Media Reports / Articles
```
[UPDATE with actual links if available]

If you have any media coverage, list:
1. [Publication Name] - "[Article Title]" - [URL] - [Date]
2. [Blog Site] - "[Post Title]" - [URL] - [Date]
3. [Tech Site] - "[Mention/Review]" - [URL] - [Date]

If no major media coverage yet:
"Currently building media presence through technical blog posts, conference presentations, and community engagement. The project focuses on organic growth through user adoption and word-of-mouth within the systems administration community."
```

### Blog Articles / Technical Writing
```
[UPDATE with actual links]

1. Official blog posts: [URL to any project blog]
2. User-written tutorials: [URLs to third-party tutorials]
3. Technical comparisons: [URLs to comparison articles]
4. Case studies: [URLs to deployment stories]

If minimal external coverage:
"The project documentation site (https://bceverly.github.io/sysmanage-docs/) serves as the primary technical resource, with comprehensive installation guides, API documentation, and configuration examples in 14 languages."
```

### GitHub Insights
```
Detailed metrics available at:
- Commit Activity: https://github.com/bceverly/sysmanage-agent/graphs/commit-activity
- Code Frequency: https://github.com/bceverly/sysmanage-agent/graphs/code-frequency
- Contributors: https://github.com/bceverly/sysmanage-agent/graphs/contributors
- Traffic: https://github.com/bceverly/sysmanage-agent/graphs/traffic
- Network: https://github.com/bceverly/sysmanage-agent/network

Key highlights:
- Sustained development activity over [X] months/years
- [X] contributors from multiple countries
- Regular release cadence (releases every [TIMEFRAME])
- Active issue triage and community support
```

### Usage Data
```
Quantifiable usage indicators:

**Download Statistics:**
- GitHub Releases: [X] total downloads
- Windows MSI (x64): [X] downloads
- Windows MSI (ARM64): [X] downloads
- macOS PKG: [X] downloads
- APT packages: [X] installs
- YUM/DNF packages: [X] installs

**Repository Engagement:**
- Repository clones (14-day): [X]
- Repository visitors (14-day): [X] unique
- Repository views (14-day): [X] total

**Dependency Usage:**
- Projects depending on SysManage: [X] (https://github.com/bceverly/sysmanage-agent/network/dependents)
- Docker Hub pulls (if applicable): [X]
- PyPI downloads (if published): [X/month]

**Documentation Access:**
- Docs site visitors/month: [X]
- Installation guide views: [X]
- Multi-language access: 14 languages supported
```

### Trademark Proof (if applicable)
```
[If you've trademarked "SysManage":]
Trademark Registration: [Registration Number]
Authority: [USPTO / WIPO / other]
Status: [Registered / Pending]
Classes: [International Classes]
Owner: [Legal entity]
Verification: [Link to trademark database]

[If not trademarked:]
"SysManage" is not currently trademarked. The project relies on its open source MIT license and GitHub repository as the authoritative source of the genuine software.
```

## Form Section 7: Technical Details

### What will be signed?
```
Windows MSI installer packages:
- sysmanage-agent-[VERSION]-windows-x64.msi
- sysmanage-agent-[VERSION]-windows-arm64.msi
```

### File Types to be Signed
```
- MSI (Microsoft Installer Package)
- EXE (if applicable for any bundled executables)
```

### Signing Frequency
```
- Every official release (following semantic versioning)
- Approximately [X] releases per quarter
- All releases published to GitHub Releases
- Packages distributed via GitHub Pages repository
```

### Build Process
```
Automated via GitHub Actions:
- Workflow: .github/workflows/build-and-release.yml
- Triggered on: Git tag push (pattern: v*)
- Build environment: windows-latest (GitHub-hosted)
- Build tool: WiX Toolset v5
- Process:
  1. Checkout code
  2. Build MSI for x64 and ARM64
  3. Generate SHA256 checksums
  4. [AFTER SIGNPATH]: Sign MSI packages
  5. Upload to GitHub Releases
  6. Deploy to GitHub Pages repository

Build is fully automated, reproducible, and auditable.
```

### CI/CD Integration
```
GitHub Actions workflow will be updated to:
1. Build unsigned MSI
2. Submit to SignPath for signing
3. Retrieve signed MSI
4. Publish signed MSI to releases

Workflow URL: https://github.com/bceverly/sysmanage-agent/blob/main/.github/workflows/build-and-release.yml
```

## Form Section 8: Contact Information

### Primary Contact Name
```
[Your Full Name]
```

### Primary Contact Email
```
[Your Email Address]
```

### Project Maintainer(s)
```
[Your Name] - Lead Developer
[If others, list them]

Contact via GitHub: https://github.com/bceverly
```

### GitHub Organization / User
```
https://github.com/bceverly
```

### Additional Contacts (Optional)
```
[Any co-maintainers or project admins]
```

## Form Section 9: Terms & Conditions

### Acknowledgment of Terms
```
☑ I have read and agree to the SignPath Foundation Terms of Use
☑ I confirm this project is eligible under the foundation's guidelines
☑ I agree to display SignPath Foundation certificate information on download pages
☑ I commit to following the code of conduct and responsible use policies
☑ I understand the certificate is issued for the public benefit
☑ I acknowledge that signed software must remain publicly downloadable
```

### Open Source Confirmation
```
☑ I confirm this project is released under an OSI-approved open source license
☑ I confirm the source code is publicly available
☑ I confirm the project is not used for commercial advantage
☑ I confirm the software is freely downloadable
☑ I confirm the project has no intention of going proprietary
```

### Legitimacy Declaration
```
☑ I confirm this software is legitimate and not malicious
☑ I confirm the software will not be used for harmful purposes
☑ I confirm I am authorized to submit this application
☑ I confirm all information provided is accurate and truthful
☑ I confirm I will notify SignPath of any material changes to the project
```

## Pre-Submission Checklist

Before submitting the application, verify:

### Documentation
- [ ] Privacy policy published and accessible
- [ ] Download pages are public and functional
- [ ] Documentation site is comprehensive
- [ ] README files are complete and accurate
- [ ] License file is present in repository

### Evidence
- [ ] GitHub repository stats are up to date
- [ ] Download statistics have been collected
- [ ] Community evidence has been gathered
- [ ] External mentions have been documented
- [ ] User testimonials have been collected (if any)

### Technical
- [ ] GitHub Actions workflow builds MSI successfully
- [ ] MSI installers work on fresh Windows installations
- [ ] SHA256 checksums are generated and published
- [ ] All download links are working
- [ ] Installation instructions are tested

### Compliance
- [ ] All links in application are valid and public
- [ ] Contact information is correct
- [ ] Project meets all eligibility criteria
- [ ] No COI issues with SignPath Foundation
- [ ] Terms of use are understood and accepted

## After Submission

### Expected Timeline
- **Submission acknowledgment**: 1-3 business days
- **Initial review**: 1-2 weeks
- **Follow-up questions**: May take 1-2 weeks per round
- **Final decision**: 2-4 weeks total (typically)
- **Certificate issuance**: 1-2 days after approval

### Possible Outcomes

**Approved**:
- Certificate issued for 1 year
- Integrate into CI/CD pipeline
- Update documentation with cert info
- Start signing releases

**Conditionally Approved**:
- May require additional evidence
- May need privacy policy updates
- May need more download page info
- Address feedback and resubmit

**Rejected**:
- Build more project notability
- Increase download/usage stats
- Get more external coverage
- Reapply in 6-12 months

### Support During Process
- **SignPath Support**: support@signpath.io
- **Questions**: Be prompt and professional in responses
- **Additional Info**: Provide quickly when requested
- **Patience**: Review process may take time

## Notes & Tips

### Application Best Practices
- ✅ Be honest about project status
- ✅ Provide comprehensive evidence
- ✅ Link to verifiable public data
- ✅ Be responsive to follow-up questions
- ✅ Demonstrate legitimate use and community

### Common Reasons for Rejection
- ❌ Insufficient notability or usage
- ❌ Privacy policy missing or inadequate
- ❌ Download pages not compliant
- ❌ Suspicious project purpose
- ❌ Incomplete or inaccurate information
- ❌ No evidence of real users
- ❌ Project appears abandoned

### Strengthening Your Application
- Gather user testimonials before applying
- Update all statistics immediately before submission
- Create OpenHub profile for additional metrics
- Get blog posts or articles written about the project
- Show consistent development activity
- Demonstrate responsive maintainership

---

**Remember**: SignPath Foundation is looking for legitimate, actively used open source projects. Be honest, provide comprehensive evidence, and demonstrate that your project serves the public good.

Good luck with your application!
