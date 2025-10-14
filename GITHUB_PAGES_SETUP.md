# 🚀 GitHub Pages Deployment Guide

This guide will help you deploy the **Firebolt AI-Powered Analytics Demos** to GitHub Pages for easy sharing.

## 📋 Prerequisites

- GitHub account
- Git installed locally
- The demo project already working locally

## 🎯 Quick Deployment Steps

### 1. Create GitHub Repository

```bash
# Initialize git if not already done
git init

# Add all files
git add .
git commit -m "Initial commit: Firebolt AI Analytics Demos with GitHub Pages"

# Create repository on GitHub (replace with your username)
# Go to https://github.com/new
# Repository name: mcp-nl-devrel
# Make it public for GitHub Pages
```

### 2. Push to GitHub

```bash
# Add remote (replace 'yourusername' with your GitHub username)
git remote add origin https://github.com/yourusername/mcp-nl-devrel.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### 3. Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** tab
3. Scroll down to **Pages** section
4. Under **Source**, select **GitHub Actions**
5. The workflow will automatically deploy your site

### 4. Access Your Site

Your site will be available at:
```
https://yourusername.github.io/mcp-nl-devrel/
```

## 🎨 Customization

### Update Repository Information

Edit these files to match your GitHub username:

1. **`docs/_config.yml`**:
```yaml
github_username: yourusername
repository: yourusername/mcp-nl-devrel
url: "https://yourusername.github.io"
```

2. **`README_GITHUB_PAGES.md`**:
- Replace all `asimkumarrout` references with your username
- Update social media links
- Customize contact information

3. **`docs/index.html`**:
- Update GitHub links in navigation and footer
- Customize social media links

### Add Your Branding

1. **Logo**: Add your logo to `docs/assets/images/logo.png`
2. **Favicon**: Add favicon files to `docs/` directory
3. **Colors**: Modify CSS variables in `docs/assets/css/style.css`

## 📊 Analytics & SEO (Optional)

### Google Analytics
Edit `docs/_config.yml`:
```yaml
google_analytics: UA-XXXXXXXX-X  # Your GA tracking ID
```

### SEO Optimization
The site includes:
- ✅ Meta tags for social sharing
- ✅ Open Graph tags
- ✅ JSON-LD structured data
- ✅ Sitemap generation
- ✅ Robots.txt

## 🔧 Advanced Configuration

### Custom Domain
1. Add `CNAME` file to `docs/` with your domain:
```
yourdomain.com
```
2. Configure DNS records with your domain provider
3. Update `docs/_config.yml` with your custom domain

### SSL Certificate
GitHub Pages automatically provides SSL for `*.github.io` domains and custom domains.

## 🛠️ Maintenance

### Update Content
1. Edit files in the `docs/` directory
2. Commit and push changes
3. GitHub Actions will automatically rebuild and deploy

### Monitor Deployment
- Check the **Actions** tab in your repository
- View build logs and deployment status
- Typical deployment time: 2-5 minutes

## 📱 Mobile Optimization

The site is fully responsive and includes:
- Mobile-first CSS design
- Touch-friendly navigation
- Optimized images and fonts
- Fast loading times

## 🚀 Performance Features

### Optimization Included
- ✅ Compressed CSS and assets
- ✅ Optimized images
- ✅ Lazy loading for content
- ✅ CDN delivery via GitHub Pages
- ✅ Browser caching headers

### Lighthouse Score Targets
- **Performance**: 90+
- **Accessibility**: 95+
- **Best Practices**: 90+
- **SEO**: 95+

## 🎯 Sharing Your Demos

Once deployed, share your demos with:

### Direct Links
```
Main Site:     https://yourusername.github.io/mcp-nl-devrel/
NL2SQL Demo:   https://yourusername.github.io/mcp-nl-devrel/demos/nl2sql.html
Agentic AI:    https://yourusername.github.io/mcp-nl-devrel/demos/agentic-ai.html
```

### Social Media
The site includes Open Graph tags for rich social media previews on:
- LinkedIn
- Twitter
- Facebook
- Slack

### Professional Use
Perfect for:
- 📧 Email signatures
- 💼 LinkedIn posts
- 🐦 Twitter threads
- 📋 Conference presentations
- 📖 Technical blog posts

## ❓ Troubleshooting

### Common Issues

**Site not loading?**
- Check GitHub Actions tab for build errors
- Ensure repository is public
- Verify Pages is enabled in Settings

**CSS/JS not loading?**
- Check file paths in HTML
- Ensure files are committed to repository
- Clear browser cache

**Images missing?**
- Verify image paths are correct
- Check file extensions match
- Ensure images are committed

### Support Resources

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Jekyll Documentation](https://jekyllrb.com/docs/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

## 📞 Get Help

If you need assistance:
1. Check the [Issues](https://github.com/asimkumarrout/mcp-nl-devrel/issues) page
2. Create a new issue with your question
3. Include your repository URL and error messages

---

**🎉 Congratulations!** Your Firebolt AI demos are now live and shareable on GitHub Pages!

**Next Steps:**
1. Share the link with colleagues and customers
2. Add it to your LinkedIn profile
3. Include in presentations and demos
4. Customize with your branding and content
