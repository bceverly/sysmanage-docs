# SignPath Foundation - Code Signing Application

This folder contains all documentation required for applying to the SignPath Foundation for free code signing of the SysManage Agent Windows MSI installer.

## Overview

SignPath Foundation provides free code signing certificates for open source projects. This ensures that Windows users can verify the authenticity and integrity of the SysManage Agent installer.

## Application Requirements

According to the [SignPath Foundation Terms of Use](https://signpath.org/terms), we need to provide:

### ✅ Required Documentation

1. **[Download Page with Signing Information](./1-download-page.md)**
   - Status: Ready (GitHub Pages + GitHub Releases)
   - Action Required: Add signing information after certificate is issued

2. **[Privacy Policy](./2-privacy-policy.md)**
   - Status: Needs review and publication
   - Action Required: Review, finalize, and add to documentation site

3. **[Wikipedia Article](./3-wikipedia-guide.md)**
   - Status: Not yet created
   - Action Required: Create Wikipedia article following provided guidelines

4. **[Project Verification & Trust Evidence](./4-verification-evidence.md)**
   - Status: In progress
   - Action Required: Gather metrics, testimonials, and usage data

## Application Process

### Phase 1: Preparation (Before Applying)

1. ✅ **Download Infrastructure**
   - GitHub Releases for distribution
   - GitHub Pages for documentation and repository
   - MSI packages built via GitHub Actions

2. 🔄 **Privacy Policy**
   - Review the draft privacy policy in `2-privacy-policy.md`
   - Make any necessary adjustments
   - Publish to main documentation site at `/docs/privacy-policy.html`

3. 📝 **Wikipedia Article** (Optional but Recommended)
   - Follow the comprehensive guide in `3-wikipedia-guide.md`
   - Create a draft article in your Wikipedia sandbox
   - Ensure notability criteria are met
   - Publish when ready

4. 📊 **Gather Evidence**
   - Collect GitHub statistics (stars, forks, downloads)
   - Document any media mentions or blog articles
   - Note any significant users or organizations
   - Update `4-verification-evidence.md` with current data

### Phase 2: Application Submission

1. **Visit**: signpath.io (check their website for current OSS application page)
2. **Complete**: OSSRequestForm-v4
3. **Submit**: Documentation from this folder

### Phase 3: Post-Approval

1. **Integrate** SignPath into GitHub Actions workflow
2. **Update** documentation with certificate information
3. **Sign** all MSI releases going forward
4. **Display** certificate details on download pages

## Documentation Files

| File | Purpose | Status |
|------|---------|--------|
| `1-download-page.md` | Download page requirements and signing info | ✅ Ready |
| `2-privacy-policy.md` | Privacy policy for user data handling | 🔄 Draft |
| `3-wikipedia-guide.md` | Step-by-step Wikipedia article creation | 📝 Guide |
| `4-verification-evidence.md` | Project trust and usage verification | 📊 Template |
| `application-form-answers.md` | Pre-filled answers for OSS form | 📋 Draft |

## Key SignPath Requirements

### Eligibility Criteria

✅ **License**: MIT (Open Source Initiative approved)
✅ **Repository**: Public GitHub repository
✅ **Distribution**: Free download available
✅ **Purpose**: System administration/monitoring (legitimate use)
✅ **No Malware**: Clean, security-focused code

### Signing Information Requirements

Once approved, the following must be displayed on download pages:

```
Code Signing Information:
- Certificate Issuer: SignPath Foundation
- Certificate Subject: SysManage
- Timestamp Server: SignPath Foundation
- Signature Algorithm: SHA256
```

## Timeline Estimate

- **Documentation Preparation**: 1-2 weeks
- **Wikipedia Article** (if pursuing): 2-4 weeks
- **Application Review**: 2-4 weeks (SignPath review time)
- **Integration**: 1 week

**Total**: Approximately 6-11 weeks

## Next Steps

1. **Immediate**: Review and finalize privacy policy
2. **Week 1**: Publish privacy policy to documentation site
3. **Week 2-3**: Gather verification evidence and metrics
4. **Week 3-4**: (Optional) Create Wikipedia article
5. **Week 4**: Submit SignPath application
6. **After Approval**: Integrate signing into CI/CD pipeline

## Support & Questions

- **SignPath Support**: support@signpath.io
- **Documentation**: Check signpath.io for latest documentation
- **Community**: SignPath Foundation community forums

## Notes

- SignPath Foundation is operated by SignPath GmbH
- Free for qualifying open source projects
- Certificates are issued for 1 year, renewable
- Must follow code of conduct and terms of use
- Signed packages must be publicly downloadable
