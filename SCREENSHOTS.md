# Screenshot Guidelines for SysManage Documentation

This guide explains how to add and update screenshots for the SysManage documentation site.

## Screenshot Requirements

### General Guidelines

- **Resolution**: Minimum 1920x1080, preferably 2560x1440 for high-DPI displays
- **Format**: PNG for UI screenshots, SVG for diagrams and logos
- **Quality**: High quality, clear text, no compression artifacts
- **Browser**: Use Chrome or Firefox with default zoom (100%)
- **Theme**: Use light theme for consistency unless demonstrating dark mode

### File Naming Convention

```text
screenshots/
├── dashboard/
│   ├── main-dashboard.png
│   ├── dashboard-hosts-view.png
│   └── dashboard-alerts.png
├── hosts/
│   ├── hosts-list.png
│   ├── host-detail.png
│   └── host-approval.png
├── updates/
│   ├── updates-overview.png
│   ├── security-updates.png
│   └── update-installation.png
├── users/
│   ├── user-management.png
│   └── user-profile.png
└── settings/
    ├── general-settings.png
    └── security-settings.png
```

## Key Screenshots Needed

### 1. Main Dashboard (`dashboard-main.png`)

- **URL**: `https://your-server:8443/`
- **Content**: Overview with host stats, recent activity, system health
- **Size**: Full browser window
- **Notes**: Should show representative data, not empty state

### 2. Host Management (`hosts-list.png`)

- **URL**: `https://your-server:8443/hosts`
- **Content**: List of hosts with various statuses
- **Size**: Full browser window
- **Notes**: Include mix of online/offline hosts, different OS types

### 3. Host Detail View (`host-detail.png`)

- **URL**: `https://your-server:8443/hosts/[host-id]`
- **Content**: Detailed host information, specs, packages
- **Size**: Full page with some scrolling visible
- **Notes**: Choose a host with interesting data

### 4. Updates Management (`updates-overview.png`)

- **URL**: `https://your-server:8443/updates`
- **Content**: Available updates across all hosts
- **Size**: Full browser window
- **Notes**: Show mix of security and regular updates

### 5. User Management (`user-management.png`)

- **URL**: `https://your-server:8443/users`
- **Content**: User list and management interface
- **Size**: Full browser window
- **Notes**: Include different user roles/permissions

### 6. Login Screen (`login.png`)

- **URL**: `https://your-server:8443/login`
- **Content**: Login form
- **Size**: Full browser window
- **Notes**: Clean, professional appearance

## Screenshot Process

### 1. Preparation

1. Set up a demo environment with representative data
2. Create test hosts with various configurations
3. Ensure some updates are available for demonstration
4. Set browser to 100% zoom
5. Use incognito/private mode for clean session

### 2. Taking Screenshots

1. Navigate to the target page
2. Wait for all content to load completely
3. Hide browser UI (F11 fullscreen, then crop)
4. Take screenshot using:
   - **macOS**: Cmd+Shift+4, then select area
   - **Windows**: Windows+Shift+S
   - **Linux**: Use GNOME Screenshot or similar tool

### 3. Post-Processing

1. Crop to remove browser chrome
2. Ensure consistent sizing (maintain aspect ratios)
3. Optimize file size without quality loss
4. Add subtle drop shadows if needed for visual appeal

## Adding Screenshots to Documentation

### 1. File Placement

- Place files in `/assets/images/screenshots/`
- Use descriptive names matching the content
- Organize in subdirectories by feature area

### 2. HTML Integration

```html
<div class="screenshot-container">
    <img src="../../assets/images/screenshots/dashboard-main.png"
         alt="SysManage Main Dashboard"
         class="screenshot">
    <div class="screenshot-caption">
        Main dashboard showing system overview, host status, and recent activity.
    </div>
</div>
```

### 3. CSS Classes Available

- `.screenshot-container`: Wrapper with border and shadow
- `.screenshot`: Basic screenshot styling
- `.screenshot-caption`: Caption styling
- `.screenshot-small`: Smaller screenshot (50% width)
- `.screenshot-mobile`: Mobile device mockup frame

## Updating Existing Screenshots

### When to Update

- UI changes significantly
- New features are added to existing pages
- Better quality versions become available
- Outdated information is shown

### Update Process

1. Replace the existing file with same filename
2. Update alt text if content changed significantly
3. Update captions if needed
4. Test that all references still work

## Demo Data Guidelines

### Hosts

- **Minimum 5 hosts** with different:
  - Operating systems (Linux, Windows, macOS, BSD)
  - Status (online, offline, warning)
  - Update counts
  - Hardware specifications

### Updates

- Mix of security and regular updates
- Different package managers represented
- Various severity levels

### Users

- Admin and regular user accounts
- Different access levels demonstrated
- Recent activity shown

## Quality Checklist

Before submitting screenshots, verify:

- [ ] High resolution and clear text
- [ ] Consistent browser/OS theme
- [ ] Representative, realistic data
- [ ] No sensitive information visible
- [ ] Proper file naming convention
- [ ] Optimized file size
- [ ] All referenced elements are visible
- [ ] Professional appearance

## Tools and Resources

### Recommended Tools

- **Screenshot**: Built-in OS tools or Lightshot
- **Editing**: GIMP, Photoshop, or Figma
- **Optimization**: TinyPNG, ImageOptim
- **Browser**: Chrome DevTools for responsive testing

### Demo Data Scripts

Check the main SysManage repository for demo data generation scripts:

- `scripts/demo-data.py` - Creates sample hosts and data
- `scripts/test-users.py` - Creates test user accounts

## Contributing

To contribute screenshots:

1. Follow this guide for consistency
2. Submit via pull request to the sysmanage-docs repository
3. Include description of what's shown in each screenshot
4. Tag screenshots with version they represent

## Maintenance

Screenshots should be reviewed and updated:

- With each major release
- When significant UI changes occur
- Annually for freshness
- When user feedback indicates confusion

---

**Note**: This documentation will evolve as the project grows. Please suggest improvements or report issues with screenshot quality or relevance.