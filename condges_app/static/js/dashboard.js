// CONDGES Dashboard JavaScript
class CondgesDashboard {
    constructor() {
        this.data = null;
        this.charts = {};
        this.currentYear = null;
        this.currentMonth = null;
        this.currentAsset = null;
        
        this.init();
    }
    
    async init() {
        console.log('🚀 Initializing CONDGES Dashboard...');
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Check API health
        await this.checkHealth();
        
        // Load initial data
        await this.loadData();
        
        // Render dashboard
        this.render();
        
        console.log('✅ Dashboard initialized successfully');
    }
    
    setupEventListeners() {
        // Year filter
        document.getElementById('year-select').addEventListener('change', (e) => {
            this.currentYear = e.target.value || null;
            this.render();
        });
        
        // Month filter
        document.getElementById('month-select').addEventListener('change', (e) => {
            this.currentMonth = e.target.value ? parseInt(e.target.value) : null;
            this.render();
        });
        
        // Asset filter
        document.getElementById('asset-select').addEventListener('change', (e) => {
            this.currentAsset = e.target.value || null;
            this.render();
        });
        
        // Refresh button
        document.getElementById('refresh-btn').addEventListener('click', () => {
            this.loadData();
        });
    }
    
    async checkHealth() {
        try {
            const response = await axios.get('/api/health');
            this.updateConnectionStatus('connected', 'Database connesso');
            console.log('✅ API Health Check passed');
        } catch (error) {
            this.updateConnectionStatus('error', 'Errore connessione');
            console.error('❌ API Health Check failed:', error);
        }
    }
    
    updateConnectionStatus(status, message) {
        const statusDot = document.getElementById('connection-status');
        const statusText = document.getElementById('status-text');
        
        statusDot.className = `status-dot ${status}`;
        statusText.textContent = message;
    }
    
    async loadData() {
        try {
            this.showLoading(true);
            
            console.log('📊 Loading dashboard data...');
            const response = await axios.get('/api/summary');
            
            if (response.data.success) {
                this.data = response.data.data;
                this.populateFilters();
                this.showLoading(false);
                console.log('✅ Data loaded successfully');
            } else {
                throw new Error(response.data.error);
            }
            
        } catch (error) {
            console.error('❌ Error loading data:', error);
            this.showError(`Errore nel caricamento dei dati: ${error.message}`);
        }
    }
    
    populateFilters() {
        // Populate year filter
        const yearSelect = document.getElementById('year-select');
        yearSelect.innerHTML = '<option value="">Tutti gli anni</option>';
        
        if (this.data.years) {
            this.data.years.forEach(year => {
                const option = document.createElement('option');
                option.value = year;
                option.textContent = year;
                yearSelect.appendChild(option);
            });
        }
        
        // Populate asset filter
        const assetSelect = document.getElementById('asset-select');
        assetSelect.innerHTML = '<option value="">Tutti gli asset</option>';
        
        if (this.data.assets) {
            Object.keys(this.data.assets).forEach(assetName => {
                const asset = this.data.assets[assetName];
                const option = document.createElement('option');
                option.value = assetName;
                option.textContent = asset.info.display_name;
                assetSelect.appendChild(option);
            });
        }
    }
    
    showLoading(show) {
        document.getElementById('loading').style.display = show ? 'flex' : 'none';
        document.getElementById('dashboard-content').style.display = show ? 'none' : 'block';
        document.getElementById('error-display').style.display = 'none';
    }
    
    showError(message) {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('dashboard-content').style.display = 'none';
        document.getElementById('error-display').style.display = 'block';
        document.getElementById('error-message').textContent = message;
    }
    
    render() {
        if (!this.data) return;
        
        console.log('🎨 Rendering dashboard...');
        
        this.renderKPIs();
        this.renderCharts();
        this.renderTables();
        
        console.log('✅ Dashboard rendered');
    }
    
    renderKPIs() {
        const kpiGrid = document.getElementById('kpi-grid');
        kpiGrid.innerHTML = '';
        
        if (!this.data.totals) return;
        
        const years = this.currentYear ? [parseInt(this.currentYear)] : this.data.years;
        const latestYear = Math.max(...years);
        const previousYear = latestYear - 1;
        
        const current = this.data.totals[latestYear];
        const previous = this.data.totals[previousYear];
        
        if (!current) return;
        
        const kpis = [
            {
                title: `Ricavi Totali ${latestYear}`,
                value: this.formatCurrency(current.ricavi_totali),
                change: previous ? this.calculateChange(current.ricavi_totali, previous.ricavi_totali) : null
            },
            {
                title: `Costi Totali ${latestYear}`,
                value: this.formatCurrency(current.costi_totali),
                change: previous ? this.calculateChange(current.costi_totali, previous.costi_totali) : null
            },
            {
                title: `Margine Totale ${latestYear}`,
                value: this.formatCurrency(current.margine_totale),
                change: previous ? this.calculateChange(current.margine_totale, previous.margine_totale) : null
            },
            {
                title: `Margine % ${latestYear}`,
                value: `${current.margine_pct.toFixed(1)}%`,
                change: previous ? `${(current.margine_pct - previous.margine_pct).toFixed(1)}pp` : null
            }
        ];
        
        kpis.forEach(kpi => {
            const card = this.createKPICard(kpi);
            kpiGrid.appendChild(card);
        });
    }
    
    createKPICard(kpi) {
        const card = document.createElement('div');
        card.className = 'kpi-card';
        
        const changeClass = kpi.change ? (kpi.change.startsWith('+') ? 'positive' : 'negative') : '';
        const changeDisplay = kpi.change || '';
        
        card.innerHTML = `
            <h4>${kpi.title}</h4>
            <div class="kpi-value">${kpi.value}</div>
            <div class="kpi-change ${changeClass}">${changeDisplay}</div>
        `;
        
        return card;
    }
    
    calculateChange(current, previous) {
        if (!previous || previous === 0) return null;
        const change = ((current - previous) / previous) * 100;
        const sign = change >= 0 ? '+' : '';
        return `${sign}${change.toFixed(1)}%`;
    }
    
    renderCharts() {
        this.renderRevenueChart();
        this.renderMarginChart();
    }
    
    renderRevenueChart() {
        const ctx = document.getElementById('revenue-chart').getContext('2d');
        
        // Destroy existing chart
        if (this.charts.revenue) {
            this.charts.revenue.destroy();
        }
        
        const datasets = [];
        const labels = ['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu', 'Lug', 'Ago', 'Set', 'Ott', 'Nov', 'Dic'];
        
        const colors = {
            'HOTEL': '#3b82f6',
            'RESIDENCE_ANGELINA': '#10b981',
            'CVM': '#f59e0b'
        };
        
        Object.keys(this.data.assets).forEach(assetName => {
            if (this.currentAsset && this.currentAsset !== assetName) return;
            
            const asset = this.data.assets[assetName];
            const year = this.currentYear || Math.max(...this.data.years);
            const yearData = asset.years[year];
            
            if (!yearData) return;
            
            const monthlyData = new Array(12).fill(0);
            yearData.months_data.forEach(month => {
                if (month.month && month.ricavi) {
                    monthlyData[month.month - 1] = parseFloat(month.ricavi);
                }
            });
            
            datasets.push({
                label: asset.info.display_name,
                data: monthlyData,
                borderColor: colors[assetName] || '#667eea',
                backgroundColor: colors[assetName] || '#667eea',
                fill: false,
                tension: 0.1
            });
        });
        
        this.charts.revenue = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return '€' + value.toLocaleString();
                            }
                        }
                    }
                }
            }
        });
    }
    
    renderMarginChart() {
        const ctx = document.getElementById('margin-chart').getContext('2d');
        
        // Destroy existing chart
        if (this.charts.margin) {
            this.charts.margin.destroy();
        }
        
        const datasets = [];
        const labels = ['Gen', 'Feb', 'Mar', 'Apr', 'Mag', 'Giu', 'Lug', 'Ago', 'Set', 'Ott', 'Nov', 'Dic'];
        
        const colors = {
            'HOTEL': '#3b82f6',
            'RESIDENCE_ANGELINA': '#10b981',
            'CVM': '#f59e0b'
        };
        
        Object.keys(this.data.assets).forEach(assetName => {
            if (this.currentAsset && this.currentAsset !== assetName) return;
            
            const asset = this.data.assets[assetName];
            const year = this.currentYear || Math.max(...this.data.years);
            const yearData = asset.years[year];
            
            if (!yearData) return;
            
            const monthlyData = new Array(12).fill(0);
            yearData.months_data.forEach(month => {
                if (month.month && month.margine_pct !== null) {
                    monthlyData[month.month - 1] = parseFloat(month.margine_pct);
                }
            });
            
            datasets.push({
                label: asset.info.display_name,
                data: monthlyData,
                backgroundColor: colors[assetName] || '#667eea',
                borderColor: colors[assetName] || '#667eea',
                borderWidth: 1
            });
        });
        
        this.charts.margin = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return value + '%';
                            }
                        }
                    }
                }
            }
        });
    }
    
    renderTables() {
        this.renderMonthlyTable();
        this.renderAnnualTable();
    }
    
    renderMonthlyTable() {
        const tbody = document.getElementById('monthly-table-body');
        tbody.innerHTML = '';
        
        const allData = [];
        
        Object.keys(this.data.assets).forEach(assetName => {
            if (this.currentAsset && this.currentAsset !== assetName) return;
            
            const asset = this.data.assets[assetName];
            
            Object.keys(asset.years).forEach(year => {
                if (this.currentYear && this.currentYear !== year) return;
                
                const yearData = asset.years[year];
                yearData.months_data.forEach(month => {
                    // Apply month filter
                    if (this.currentMonth && month.month !== this.currentMonth) return;
                    
                    if (month.ricavi > 0 || month.costi_totale > 0) {
                        allData.push({
                            asset: asset.info.display_name,
                            year: year,
                            month: month.month_name,
                            ...month
                        });
                    }
                });
            });
        });
        
        // Sort by year desc, then month desc
        allData.sort((a, b) => {
            if (a.year !== b.year) return b.year - a.year;
            return b.month - a.month;
        });
        
        allData.forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${row.asset}</td>
                <td>${row.year}</td>
                <td>${row.month_name}</td>
                <td>${this.formatCurrency(row.ricavi)}</td>
                <td>${this.formatCurrency(row.costi_personale)}</td>
                <td>${this.formatCurrency(row.costi_produzione)}</td>
                <td>${this.formatCurrency(row.costi_gestione)}</td>
                <td>${this.formatCurrency(row.costi_commerciale)}</td>
                <td>${this.formatCurrency(row.costi_totale)}</td>
                <td class="${row.margine >= 0 ? 'positive' : 'negative'}">${this.formatCurrency(row.margine)}</td>
                <td class="${row.margine_pct >= 0 ? 'positive' : 'negative'}">${row.margine_pct.toFixed(1)}%</td>
            `;
            tbody.appendChild(tr);
        });
    }
    
    renderAnnualTable() {
        const tbody = document.getElementById('annual-table-body');
        tbody.innerHTML = '';
        
        const allData = [];
        
        Object.keys(this.data.assets).forEach(assetName => {
            if (this.currentAsset && this.currentAsset !== assetName) return;
            
            const asset = this.data.assets[assetName];
            
            Object.keys(asset.years).forEach(year => {
                if (this.currentYear && this.currentYear !== year) return;
                
                const yearData = asset.years[year];
                allData.push({
                    asset: asset.info.display_name,
                    year: year,
                    ...yearData
                });
            });
        });
        
        // Sort by year desc
        allData.sort((a, b) => b.year - a.year);
        
        allData.forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${row.asset}</td>
                <td>${row.year}</td>
                <td>${this.formatCurrency(row.ricavi_annuali)}</td>
                <td>${this.formatCurrency(row.costi_annuali)}</td>
                <td class="${row.margine_annuale >= 0 ? 'positive' : 'negative'}">${this.formatCurrency(row.margine_annuale)}</td>
                <td class="${row.margine_pct >= 0 ? 'positive' : 'negative'}">${row.margine_pct.toFixed(1)}%</td>
            `;
            tbody.appendChild(tr);
        });
    }
    
    formatCurrency(value) {
        return new Intl.NumberFormat('it-IT', {
            style: 'currency',
            currency: 'EUR',
            minimumFractionDigits: 0,
            maximumFractionDigits: 0
        }).format(value);
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new CondgesDashboard();
});
