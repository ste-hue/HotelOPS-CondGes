#!/usr/bin/env python3
"""
CONDGES Flask Dashboard Application
Dynamic hotel financial dashboard with Supabase backend
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from supabase import create_client, Client
import os
import json
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supabase configuration
SUPABASE_URL = "https://udeavsfewakatewsphfw.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVkZWF2c2Zld2FrYXRld3NwaGZ3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTM2OTU2MzIsImV4cCI6MjA2OTI3MTYzMn0.7JuPSYEG-UoxvmYecVUgjWIAJ0PQYHeN2wiTnYp2NjY"

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'condges-hotel-dashboard-2025'
CORS(app)

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Load CONDGES data
def load_condges_data():
    """Load CONDGES financial data from JSON"""
    try:
        json_path = './data/CONDGES_ALLOCAZIONE_COMPLETA_PER_ASSET.json'
        if os.path.exists(json_path):
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            logger.warning(f"CONDGES data file not found: {json_path}")
            return None
    except Exception as e:
        logger.error(f"Error loading CONDGES data: {e}")
        return None

class CondgesAPI:
    """API class for CONDGES data operations"""
    
    @staticmethod
    def get_assets():
        """Get all assets"""
        try:
            response = supabase.table('condges_assets').select('*').order('name').execute()
            return {'success': True, 'data': response.data}
        except Exception as e:
            logger.error(f"Error fetching assets: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_monthly_data(year=None, asset_name=None):
        """Get monthly financial data with optional filters"""
        try:
            query = supabase.table('condges_dashboard_data').select('*')
            
            if year:
                query = query.eq('year', year)
            if asset_name:
                query = query.eq('asset_name', asset_name)
                
            response = query.order('year', desc=True).order('month', desc=True).execute()
            return {'success': True, 'data': response.data}
        except Exception as e:
            logger.error(f"Error fetching monthly data: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_annual_summaries():
        """Get annual summaries for all assets"""
        try:
            response = supabase.table('condges_annual_summaries').select('''
                *,
                condges_assets(name, display_name, asset_type, units_count, units_type)
            ''').order('year', desc=True).execute()
            return {'success': True, 'data': response.data}
        except Exception as e:
            logger.error(f"Error fetching annual summaries: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_dashboard_summary():
        """Get comprehensive dashboard summary"""
        try:
            # Get all data
            monthly_response = supabase.table('condges_dashboard_data').select('*').execute()
            assets_response = supabase.table('condges_assets').select('*').execute()
            
            monthly_data = monthly_response.data
            assets_data = assets_response.data
            
            # Process data by year and asset
            summary = {
                'years': [],
                'assets': {},
                'totals': {}
            }
            
            # Get unique years
            years = sorted(list(set([row['year'] for row in monthly_data if row['year']])), reverse=True)
            summary['years'] = years
            
            # Process by asset and year
            for asset in assets_data:
                asset_name = asset['name']
                summary['assets'][asset_name] = {
                    'info': asset,
                    'years': {}
                }
                
                for year in years:
                    year_data = [row for row in monthly_data if row['asset_name'] == asset_name and row['year'] == year]
                    
                    total_ricavi = sum([float(row['ricavi'] or 0) for row in year_data])
                    total_costi = sum([float(row['costi_totale'] or 0) for row in year_data])
                    total_margine = total_ricavi - total_costi
                    margine_pct = (total_margine / total_ricavi * 100) if total_ricavi > 0 else 0
                    
                    summary['assets'][asset_name]['years'][year] = {
                        'ricavi_annuali': total_ricavi,
                        'costi_annuali': total_costi,
                        'margine_annuale': total_margine,
                        'margine_pct': margine_pct,
                        'months_data': year_data
                    }
            
            # Calculate group totals
            for year in years:
                total_ricavi = sum([
                    summary['assets'][asset]['years'][year]['ricavi_annuali'] 
                    for asset in summary['assets']
                ])
                total_costi = sum([
                    summary['assets'][asset]['years'][year]['costi_annuali'] 
                    for asset in summary['assets']
                ])
                total_margine = total_ricavi - total_costi
                margine_pct = (total_margine / total_ricavi * 100) if total_ricavi > 0 else 0
                
                summary['totals'][year] = {
                    'ricavi_totali': total_ricavi,
                    'costi_totali': total_costi,
                    'margine_totale': total_margine,
                    'margine_pct': margine_pct
                }
            
            return {'success': True, 'data': summary}
            
        except Exception as e:
            logger.error(f"Error generating dashboard summary: {e}")
            return {'success': False, 'error': str(e)}

# Routes
@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/assets')
def api_assets():
    """API endpoint for assets data"""
    return jsonify(CondgesAPI.get_assets())

@app.route('/api/monthly')
def api_monthly():
    """API endpoint for monthly data"""
    year = request.args.get('year', type=int)
    asset_name = request.args.get('asset')
    return jsonify(CondgesAPI.get_monthly_data(year, asset_name))

@app.route('/api/annual')
def api_annual():
    """API endpoint for annual summaries"""
    return jsonify(CondgesAPI.get_annual_summaries())

@app.route('/api/summary')
def api_summary():
    """API endpoint for dashboard summary"""
    return jsonify(CondgesAPI.get_dashboard_summary())

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        response = supabase.table('condges_assets').select('count').execute()
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'database': 'connected'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'timestamp': datetime.now().isoformat(),
            'error': str(e)
        }), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info("🚀 Starting CONDGES Dashboard...")
    logger.info(f"📊 Supabase URL: {SUPABASE_URL}")
    
    # Test database connection on startup
    try:
        test_response = supabase.table('condges_assets').select('count').execute()
        logger.info("✅ Database connection successful")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
    
    # Run the app
    port = int(os.environ.get('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=True
    )
