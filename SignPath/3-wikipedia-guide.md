# Wikipedia Article Creation Guide for SysManage

## Overview

Creating a Wikipedia article for SysManage is **optional but highly recommended** for the SignPath Foundation application. A Wikipedia article significantly strengthens the application by demonstrating project notability and community recognition.

## ⚠️ Important Disclaimers

### Notability Requirements

Wikipedia has strict notability guidelines. Your project must have:
- **Significant coverage** in independent, reliable sources
- **Multiple independent sources** (not written by project contributors)
- **Sustained coverage** over time (not just announcement posts)

### Conflict of Interest

- You have a **conflict of interest** (COI) as the project creator
- You should **NOT create the article yourself** directly
- Instead, use the **Articles for Creation (AfC)** process
- Or request help from experienced Wikipedia editors

### Reality Check

- Most software projects do **NOT** meet Wikipedia's notability criteria
- Even well-established open source projects often lack Wikipedia articles
- Rejection is common and **does not reflect project quality**
- SignPath **does not require** a Wikipedia article; it's just helpful evidence

## Assessment: Does SysManage Meet Notability Criteria?

### Wikipedia Notability Guideline for Software

From [Wikipedia:Notability (software)](https://en.wikipedia.org/wiki/Wikipedia:Notability_(software)):

A software product is notable if it has been the subject of **significant coverage** in **independent**, **reliable sources**.

### Current Status Assessment

❓ **Questionable** - Likely does NOT yet meet Wikipedia criteria unless:

**Required (at least 2-3 of these)**:
- [ ] Coverage in major technology publications (TechCrunch, Ars Technica, etc.)
- [ ] Academic papers citing or using the software
- [ ] Books or book chapters discussing the software
- [ ] Significant media coverage beyond announcement posts
- [ ] Industry awards or recognition
- [ ] Widespread deployment in notable organizations
- [ ] Significant impact on the field

**Warning Signs That You're Not Ready**:
- ❌ Only sources are your own blog posts/announcements
- ❌ Only mentions are in software directories/listings
- ❌ No independent analysis or reviews
- ❌ Project is less than 2-3 years old
- ❌ Limited download/usage statistics

## Alternative: Wait and Build Notability

### Better Strategy for Now

Instead of rushing to Wikipedia, **build notability first**:

1. **Publish in Tech Media**
   - Write guest posts for DevOps/SysAdmin blogs
   - Submit to: OSNews, Linux Journal, AdminMagazine
   - Pitch to: The New Stack, InfoWorld, ZDNet

2. **Academic Engagement**
   - Submit papers to conferences (USENIX LISA, SREcon)
   - Publish case studies
   - Collaborate with university CS departments

3. **Community Building**
   - Present at conferences
   - Create webinars and workshops
   - Build case studies from users
   - Get testimonials from organizations

4. **Awards and Recognition**
   - Submit to open source awards
   - Apply for grants (Linux Foundation, etc.)
   - Get recognized by industry organizations

**Timeline**: Plan for 1-2 years of building notability before attempting Wikipedia

## If You Decide to Proceed Anyway

### Step-by-Step Process

#### Step 1: Create Wikipedia Account

1. Go to: https://en.wikipedia.org/wiki/Special:CreateAccount
2. Choose a username (preferably your real name)
3. Verify email address
4. Complete your user page with COI disclosure

#### Step 2: Declare Conflict of Interest

On your user page, add:

```wiki
{{COI|SysManage}}
I am the creator/maintainer of SysManage and have a conflict of interest. I will follow Wikipedia's COI guidelines and use the Articles for Creation process for any content related to this project.
```

#### Step 3: Learn Wikipedia Basics

**Required Reading** (seriously, read these):
- [Five Pillars](https://en.wikipedia.org/wiki/Wikipedia:Five_pillars)
- [Notability Guidelines](https://en.wikipedia.org/wiki/Wikipedia:Notability)
- [Conflict of Interest](https://en.wikipedia.org/wiki/Wikipedia:Conflict_of_interest)
- [Verifiability](https://en.wikipedia.org/wiki/Wikipedia:Verifiability)
- [Neutral Point of View](https://en.wikipedia.org/wiki/Wikipedia:Neutral_point_of_view)
- [Reliable Sources](https://en.wikipedia.org/wiki/Wikipedia:Reliable_sources)

#### Step 4: Gather Sources

**What Counts as a Reliable Source**:
✅ Major newspapers and magazines
✅ Academic journals and books
✅ Established technology publications
✅ Independent reviews and analyses

**What Does NOT Count**:
❌ Your own website/blog
❌ Press releases
❌ Social media posts
❌ GitHub repository
❌ Software directories/listings
❌ User-generated content (Reddit, forums)

**Minimum Required**: 2-3 independent, reliable sources with **significant coverage** (not just mentions)

#### Step 5: Create Draft in Sandbox

1. Go to your sandbox: https://en.wikipedia.org/wiki/Special:MyPage/sandbox
2. Write the article draft following the template below
3. **Be neutral**: Write as if someone else is describing your project
4. **Cite everything**: Every statement needs a reliable source
5. **No promotional language**: Avoid "best," "leading," "innovative," etc.

### Article Template

```wiki
{{AfC submission|t||ts=20250119000000|u=YourUsername|ns=118}}
{{COI|SysManage}}

'''SysManage''' is a [[free and open-source software|free and open-source]] [[system administration]] and [[Computer monitoring|monitoring]] platform for managing computer systems across multiple [[operating system]]s.<ref>{{cite web |url=https://github.com/bceverly/sysmanage-agent |title=SysManage Agent GitHub Repository |access-date=2025-01-19}}</ref>

==History==
SysManage was created in [YEAR] by [CREATOR NAME] to [PURPOSE/PROBLEM IT SOLVES].<ref>[RELIABLE SOURCE CITATION]</ref> The project was released under the [[MIT License]] and has since [DEVELOPMENT HISTORY FROM RELIABLE SOURCES].<ref>[RELIABLE SOURCE CITATION]</ref>

==Features==
SysManage provides the following capabilities:
* [[System monitoring]] across multiple operating systems
* [[Configuration management]] and policy enforcement
* [[Software deployment]] and inventory management
* [[Security]] compliance monitoring

<ref>[RELIABLE SOURCE DESCRIBING FEATURES]</ref>

==Technical details==
SysManage consists of:
* A Python-based agent that runs on managed systems
* A central server for coordination and reporting
* Support for [[Linux]], [[Microsoft Windows|Windows]], [[macOS]], and [[BSD]] operating systems

<ref>[RELIABLE SOURCE FOR TECHNICAL DETAILS]</ref>

==Reception==
[ONLY INCLUDE IF YOU HAVE RELIABLE SOURCES REVIEWING/ANALYZING THE SOFTWARE]

According to [PUBLICATION NAME], [NEUTRAL DESCRIPTION OF WHAT THEY SAID].<ref>[CITATION]</ref>

==See also==
* [[Systems management]]
* [[List of system management systems]]
* [[Comparison of system monitoring software]]

==References==
{{reflist}}

==Screenshots==
[[File:SysManage-Main-Dashboard.png|thumb|300px|SysManage main dashboard and documentation site]]

==External links==
* [https://github.com/bceverly/sysmanage-agent Official repository]
* [https://bceverly.github.io/sysmanage-docs/ Official documentation]

[[Category:Free system administration software]]
[[Category:Free software programmed in Python]]
[[Category:Cross-platform free software]]
[[Category:System administration]]
[[Category:Network management]]
```

#### Step 6: Add Screenshot (Optional but Recommended)

Wikipedia allows screenshots of software to illustrate articles. For SysManage, you can use a screenshot of the main GitHub Pages documentation site.

**How to Add Screenshot:**

1. **Take Screenshot**
   - Visit: https://bceverly.github.io/sysmanage-docs/
   - Take a clean screenshot of the main dashboard/index page
   - Recommended size: 1200px width or larger
   - Format: PNG (preferred) or JPG
   - Filename: `SysManage-Main-Dashboard.png`

2. **Upload to Wikimedia Commons**
   - Go to: https://commons.wikimedia.org/wiki/Special:UploadWizard
   - Login with your Wikipedia account
   - Upload your screenshot
   - **Title**: "SysManage-Main-Dashboard.png"
   - **Description**: "Screenshot of SysManage documentation main page showing project overview and features"
   - **License**: Select "This is my own work" and choose:
     - **Creative Commons Attribution-ShareAlike 4.0** (CC-BY-SA 4.0)
     - OR if you want more permissive: **CC0 (Public Domain)**
   - **Categories**: Add "System administration software screenshots"
   - Complete upload

3. **Add to Article**
   - Once uploaded, the screenshot is automatically available
   - Already included in template above:
     ```wiki
     ==Screenshots==
     [[File:SysManage-Main-Dashboard.png|thumb|300px|SysManage main dashboard and documentation site]]
     ```
   - The `thumb` parameter makes it a thumbnail
   - `300px` sets the width
   - The caption appears below the image

**Screenshot Guidelines:**
- ✅ Show actual software interface or documentation
- ✅ Clean, professional appearance
- ✅ No personal information visible
- ✅ High quality (not blurry)
- ✅ Representative of current version
- ❌ No promotional text or marketing material
- ❌ No watermarks or branding overlays

#### Step 7: Submit for Review

1. Once your draft is complete (with optional screenshot), submit it via **Articles for Creation**
2. Add to the top of your sandbox:
   ```wiki
   {{subst:submit}}
   ```
3. Wait for reviewer feedback (can take weeks or months)
4. Be prepared for rejection or requests for more sources

#### Step 8: Respond to Feedback

- **If accepted**: Congratulations! Maintain the article neutrally
- **If declined**: Read feedback carefully, gather more sources, improve notability
- **If deleted**: Accept it and focus on building project notability

## Alternative: Request Article from Community

### Wikipedia Request Page

If you have sources but don't want to write it yourself:

1. Go to: https://en.wikipedia.org/wiki/Wikipedia:Requested_articles
2. Post a request with your sources
3. Wait for an experienced editor to take interest
4. This is slower but avoids COI issues

### WikiProject Software

1. Visit: https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Software
2. Post on the talk page asking if anyone would review your sources
3. See if the project meets notability criteria
4. Request help creating the article if viable

## What SignPath Really Needs

### For SignPath Application

SignPath Foundation asks for:
> "The article about your project on the English Wikipedia. The article must be about your specific version of the project (same maintainer, fork etc.)"

**Reality**: This is listed as beneficial evidence but **not required**

**Better approach for new projects**:
- Focus on other verification evidence (GitHub stats, downloads, media mentions)
- Note in application: "No Wikipedia article yet; project is building notability through [X, Y, Z]"
- Provide links to any media coverage, blog posts, or analyses
- Show download statistics and GitHub metrics instead

### SignPath Will Understand

SignPath Foundation reviews **many** open source projects. They understand:
- Most software lacks Wikipedia articles
- Notability takes time to build
- GitHub stats and user testimonials are valid evidence
- Active development and real users matter more than Wikipedia

## Timeline Recommendation

### Short-term (For SignPath Application)

✅ **DO NOW**:
- Focus on other evidence (document #4)
- Gather GitHub statistics
- Collect user testimonials
- Document downloads/deployments
- Get blog post mentions

❌ **DON'T NOW**:
- Try to force a Wikipedia article
- Risk rejection and delay
- Waste time on likely-to-fail attempt

### Long-term (Building Notability)

📅 **Year 1-2**:
- Build user base
- Get media coverage
- Present at conferences
- Publish case studies
- Grow community

📅 **Year 2-3**:
- Reassess notability
- Gather independent sources
- Consider Wikipedia attempt
- Or hire Wikipedia expert

## Professional Wikipedia Services

If you're serious about Wikipedia later:

### Wikipedia Editing Services (COI-Compliant)

Companies that help with COI-compliant article creation:
- WikiExperts
- The Wikipedia Help
- WikiCreationInc

**Cost**: $500-$2000 typically
**Time**: 1-3 months
**Success**: Not guaranteed; depends on sources

### University Students

- Computer science students doing projects
- Technical writing students
- Offer co-authorship on a paper in exchange

## Conclusion

### Honest Assessment

For a new project like SysManage:
- ❌ **Probably not ready** for Wikipedia yet
- ✅ **Perfectly fine** for SignPath application anyway
- 📈 **Focus on building** real-world use and coverage
- ⏰ **Revisit in 1-2 years** after establishing notability

### Recommended Action

**For SignPath Application RIGHT NOW**:

1. ❌ **Skip Wikipedia** - Not worth the effort/risk
2. ✅ **Focus on Document #4** - Verification evidence
3. ✅ **Gather real metrics** - Downloads, users, deployments
4. ✅ **Get testimonials** - From actual users
5. ✅ **Note in application**: "Building notability; no Wikipedia article yet"

**For Long-term Project Growth**:

1. Build real user base
2. Get independent media coverage
3. Establish industry presence
4. Revisit Wikipedia in 2026-2027

## Questions?

- **Wikipedia Help Desk**: https://en.wikipedia.org/wiki/Wikipedia:Help_desk
- **WikiProject Software**: https://en.wikipedia.org/wiki/Wikipedia:WikiProject_Software
- **Articles for Creation Help**: https://en.wikipedia.org/wiki/Wikipedia:AFC_help

---

*This guide provides an honest, realistic assessment of Wikipedia notability requirements. Most new open source projects do NOT meet these criteria, and that's completely normal and acceptable.*
