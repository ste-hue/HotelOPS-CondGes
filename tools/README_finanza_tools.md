
# 🏨 ORTI Finance Dashboard

> Modern financial management system for hospitality businesses with real-time analytics and mobile-first design.

## ✨ Features

### 📊 **Financial Analytics**
- **Real-time Revenue Tracking** - Monitor income from multiple properties (CVM, Angelina Residence, Hotel Panorama)
- **Expense Management** - Categorize and track operational costs
- **Cash Flow Analysis** - Complete financial overview with automated calculations
- **Monthly Projections** - Forward-looking financial planning

### 🔐 **Enterprise Security**
- **Google OAuth Integration** - Secure single sign-on authentication
- **Domain-based Access Control** - Restrict access to authorized company domains
- **Row Level Security** - Database-level data protection
- **Audit Trail** - Complete logging of all financial operations

### 📱 **Mobile-First Design**
- **Responsive Dashboard** - Optimized for all screen sizes
- **Touch-Friendly Interface** - 44px minimum touch targets (iOS compliant)
- **Dark Mode Support** - Automatic theme switching
- **Offline-Ready** - Progressive Web App capabilities

### 🏢 **Multi-Property Management**
- **Property Separation** - Individual tracking for each location
- **Consolidated Reporting** - Combined analytics across properties
- **Category Management** - Flexible income/expense categorization
- **Historical Data** - Year-over-year comparison and trending

## 🚀 Live Demo

**Production URL**: [Coming Soon - Cloudflare Pages]

### Test Accounts
- Access restricted to `@panoramagroup.it` domains and authorized users
- Contact administrator for access

## 🛠️ Technology Stack

### Frontend
- **React 18** + **TypeScript** - Modern component architecture
- **Vite** - Lightning-fast build tool
- **Tailwind CSS** - Utility-first styling
- **shadcn/ui** - High-quality component library
- **Recharts** - Interactive financial charts

### Backend & Database  
- **Supabase** - PostgreSQL database with real-time subscriptions
- **Row Level Security (RLS)** - Database-level authorization
- **Real-time Updates** - Live data synchronization across clients

### Authentication & Security
- **Google OAuth 2.0** - Enterprise authentication
- **Domain Restrictions** - Company-specific access control
- **End-to-End Encryption** - Secure data transmission

### Deployment
- **Cloudflare Pages** - Global CDN deployment
- **GitHub Actions** - Automated CI/CD pipeline
- **Progressive Web App** - Mobile app experience

## 📦 Installation

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Supabase account (for database)
- Google Cloud Console (for OAuth)

### Local Development

```bash
# Clone repository
git clone https://github.com/ste-hue/finanza.git
cd finanza/orti-finance-compass

# Install dependencies  
npm install

# Start development server
npm run dev
```

Visit `http://localhost:8080`

### Environment Setup

The application uses Supabase for backend services. Database configuration is handled through the Supabase client setup.

## 🔧 Configuration

### Google OAuth Setup

1. **Google Cloud Console**:
   - Create OAuth 2.0 Client ID
   - Add authorized domains
   - Configure redirect URIs

2. **Supabase Dashboard**:
   - Enable Google provider
   - Add Client ID and Secret
   - Configure authentication settings

### Database Schema

Key tables:
- `companies` - Business entities
- `categories` - Income/expense categories  
- `subcategories` - Detailed category breakdown
- `entries` - Financial transactions
- `authorized_users` - Access control

## 📊 Usage

### Dashboard Overview
- **Monthly summaries** for all properties
- **Real-time totals** with live updates
- **Interactive charts** for trend analysis
- **Export capabilities** for reporting

### Data Management
- **Bulk import** from Excel files
- **Manual entry** through intuitive forms
- **Category management** with drag-and-drop ordering
- **Data validation** with automated checks

### Mobile Experience  
- **Bottom navigation** for easy thumb access
- **Swipe gestures** for data interaction
- **Optimized forms** for mobile input
- **Offline sync** for unreliable connections

## 🔐 Security Features

### Access Control
```typescript
// Domain-based restrictions
const authorizedDomains = [
  '@panoramagroup.it',
  'stedepi@gmail.com'
];
```

### Data Protection
- All financial data protected by RLS policies
- Real-time audit logging
- Encrypted data transmission
- Secure session management

## 🚀 Deployment

### Cloudflare Pages Setup

```bash
# Build for production
npm run build

# Deploy automatically via Git push
git push origin master
```

**Build Configuration**:
- **Framework**: Vite
- **Build Command**: `npm run build`
- **Output Directory**: `dist`
- **Root Directory**: `orti-finance-compass`

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Guidelines
- Follow TypeScript strict mode
- Use semantic commit messages
- Ensure mobile responsiveness
- Add tests for financial calculations
- Document complex business logic

## 📄 License

This project is private and proprietary to ORTI/Panorama Group.

## 🆘 Support

For technical support or feature requests:
- **Email**: [Contact Information]
- **Issues**: GitHub Issues (for authorized contributors)
- **Documentation**: [Internal Wiki Link]

## 🏆 Acknowledgments

- **ORTI Team** - Business requirements and testing
- **Panorama Group** - Financial data and domain expertise  
- **Supabase** - Backend infrastructure
- **Cloudflare** - Global deployment platform

---

**Made with ❤️ for modern hospitality financial management**
