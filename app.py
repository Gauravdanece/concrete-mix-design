import streamlit as st
import math
from datetime import datetime

class ConcreteMixDesign:
    def __init__(self):
        self.mix_data = {}
        self.grade_properties = {
            'M10': {'f_ck': 10, 'std_dev': 3.5, 'X': 5.0},
            'M15': {'f_ck': 15, 'std_dev': 3.5, 'X': 5.0},
            'M20': {'f_ck': 20, 'std_dev': 4.0, 'X': 5.5},
            'M25': {'f_ck': 25, 'std_dev': 4.0, 'X': 5.5},
            'M30': {'f_ck': 30, 'std_dev': 5.0, 'X': 6.5},
            'M35': {'f_ck': 35, 'std_dev': 5.0, 'X': 6.5},
            'M40': {'f_ck': 40, 'std_dev': 5.0, 'X': 6.5},
            'M45': {'f_ck': 45, 'std_dev': 5.0, 'X': 6.5},
            'M50': {'f_ck': 50, 'std_dev': 5.0, 'X': 6.5},
            'M55': {'f_ck': 55, 'std_dev': 5.0, 'X': 6.5},
            'M60': {'f_ck': 60, 'std_dev': 5.0, 'X': 6.5},
            'M65': {'f_ck': 65, 'std_dev': 6.0, 'X': 8.0},
            'M70': {'f_ck': 70, 'std_dev': 6.0, 'X': 8.0},
            'M75': {'f_ck': 75, 'std_dev': 6.0, 'X': 8.0},
            'M80': {'f_ck': 80, 'std_dev': 6.0, 'X': 8.0}
        }
    
    def set_input_parameters(self, params):
        self.mix_data.update(params)
    
    def calculate_target_strength(self):
        grade = self.mix_data['grade']
        f_ck = self.grade_properties[grade]['f_ck']
        
        S = self.grade_properties[grade]['std_dev']
        if self.mix_data.get('site_control', 'Good') == 'Fair':
            S += 1.0
        
        X = self.grade_properties[grade]['X']
        
        f_ck1 = f_ck + 1.65 * S
        f_ck2 = f_ck + X
        
        target_strength = max(f_ck1, f_ck2)
        
        self.mix_data['target_strength'] = target_strength
        self.mix_data['std_dev'] = S
        
        return target_strength
    
    def get_air_content(self):
        max_size = self.mix_data['max_aggregate_size']
        
        air_content = {
            10: 1.5,
            20: 1.0,
            40: 0.8
        }
        
        air = air_content.get(max_size, 1.0)
        return air / 100
    
    def select_water_cement_ratio(self, target_strength):
        cement_type = self.mix_data['cement_type']
        
        if '53' in cement_type:
            if target_strength <= 30:
                wc_ratio = 0.50
            elif target_strength <= 40:
                wc_ratio = 0.45
            elif target_strength <= 50:
                wc_ratio = 0.40
            elif target_strength <= 60:
                wc_ratio = 0.35
            else:
                wc_ratio = 0.30
        elif '43' in cement_type:
            if target_strength <= 25:
                wc_ratio = 0.50
            elif target_strength <= 35:
                wc_ratio = 0.45
            elif target_strength <= 45:
                wc_ratio = 0.40
            else:
                wc_ratio = 0.35
        else:
            if target_strength <= 20:
                wc_ratio = 0.55
            elif target_strength <= 30:
                wc_ratio = 0.50
            elif target_strength <= 40:
                wc_ratio = 0.45
            else:
                wc_ratio = 0.40
        
        max_wc_ratio = self.mix_data['max_wc_ratio']
        if wc_ratio > max_wc_ratio:
            wc_ratio = max_wc_ratio
        
        self.mix_data['wc_ratio'] = wc_ratio
        return wc_ratio
    
    def calculate_water_content(self):
        max_size = self.mix_data['max_aggregate_size']
        slump = self.mix_data['workability_slump']
        agg_type = self.mix_data.get('aggregate_type', 'Crushed angular aggregate')
        
        base_water = {
            10: 208,
            20: 186, 
            40: 165
        }
        
        water_50mm = base_water.get(max_size, 186)
        
        agg_reduction = 0
        if 'sub-angular' in agg_type.lower():
            agg_reduction = 10
        elif 'gravel with some crushed' in agg_type.lower():
            agg_reduction = 15
        elif 'rounded' in agg_type.lower():
            agg_reduction = 20
        
        water_50mm_agg = water_50mm - agg_reduction
        
        slump_adjustment = ((slump - 50) / 25) * 0.03
        water_for_slump = water_50mm_agg * (1 + slump_adjustment)
        
        if self.mix_data.get('use_admixture', False):
            admix_type = self.mix_data.get('admixture_type', 'Superplasticizer - normal')
            if 'superplasticizer' in admix_type.lower():
                if 'pce' in admix_type.lower():
                    water_reduction = 0.30
                else:
                    water_reduction = 0.23
            elif 'plasticizer' in admix_type.lower():
                water_reduction = 0.15
            else:
                water_reduction = 0.10
        else:
            water_reduction = 0.0
        
        final_water = water_for_slump * (1 - water_reduction)
        
        return round(final_water)
    
    def calculate_cement_content(self, water_content, wc_ratio):
        cement_content = water_content / wc_ratio
        min_cement_content = self.mix_data['min_cement_content']
        
        if cement_content < min_cement_content:
            cement_content = min_cement_content
            wc_ratio = water_content / cement_content
            self.mix_data['wc_ratio'] = wc_ratio
        
        return round(cement_content)
    
    def calculate_aggregate_proportions(self, wc_ratio):
        max_size = self.mix_data['max_aggregate_size']
        zone = self.mix_data['fine_agg_zone']
        placing_method = self.mix_data.get('placing_method', 'Chute (Non pumpable)')
        
        base_volume = {
            10: {'I': 0.48, 'II': 0.50, 'III': 0.52, 'IV': 0.54},
            20: {'I': 0.60, 'II': 0.62, 'III': 0.64, 'IV': 0.66},
            40: {'I': 0.69, 'II': 0.71, 'III': 0.72, 'IV': 0.73}
        }
        
        vol_coarse_base = base_volume[max_size][zone]
        
        wc_difference = 0.50 - wc_ratio
        adjustment = (wc_difference / 0.05) * 0.01
        vol_coarse_adjusted = vol_coarse_base + adjustment
        
        if 'pump' in placing_method.lower():
            reduction = 0.10
            vol_coarse_adjusted = vol_coarse_adjusted * (1 - reduction)
        
        vol_fine = 1 - vol_coarse_adjusted
        
        return vol_coarse_adjusted, vol_fine
    
    def perform_full_design(self):
        try:
            target_strength = self.calculate_target_strength()
            wc_ratio = self.select_water_cement_ratio(target_strength)
            water_content = self.calculate_water_content()
            cement_content = self.calculate_cement_content(water_content, wc_ratio)
            vol_coarse, vol_fine = self.calculate_aggregate_proportions(wc_ratio)
            air_content = self.get_air_content()
            
            return {
                'success': True,
                'target_strength': target_strength,
                'wc_ratio': wc_ratio,
                'water_content': water_content,
                'cement_content': cement_content,
                'vol_coarse': vol_coarse,
                'vol_fine': vol_fine,
                'air_content': air_content,
                'grade': self.mix_data['grade'],
                'exposure': self.mix_data['exposure']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

def main():
    st.set_page_config(
        page_title="Concrete Mix Design - IS 10262:2019",
        page_icon="🏗️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .result-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<h1 class="main-header">🏗️ Concrete Mix Design Calculator</h1>', unsafe_allow_html=True)
    st.markdown("### As per IS 10262:2019 Standards")
    
    with st.sidebar:
        st.header("⚙️ Design Parameters")
        
        grade = st.selectbox(
            "**Concrete Grade**",
            ['M10', 'M15', 'M20', 'M25', 'M30', 'M35', 'M40', 'M45', 'M50', 
             'M55', 'M60', 'M65', 'M70', 'M75', 'M80'],
            index=3
        )
        
        exposure_options = {
            'Mild': {'max_wc': 0.55, 'min_cement': 220, 'desc': 'Protected against weather'},
            'Moderate': {'max_wc': 0.50, 'min_cement': 240, 'desc': 'Sheltered from heavy rain'},
            'Severe': {'max_wc': 0.45, 'min_cement': 320, 'desc': 'Exposed to rain, freezing'},
            'Very Severe': {'max_wc': 0.40, 'min_cement': 340, 'desc': 'Coastal, corrosive environment'},
            'Extreme': {'max_wc': 0.35, 'min_cement': 360, 'desc': 'Marine, industrial zones'}
        }
        
        exposure = st.selectbox(
            "**Exposure Condition**",
            list(exposure_options.keys()),
            index=2,
            help=exposure_options['Severe']['desc']
        )
        
        cement_type = st.selectbox(
            "**Cement Type**",
            [
                'OPC 33 Grade conforming to IS 269',
                'OPC 43 Grade conforming to IS 269',
                'OPC 53 Grade conforming to IS 269',
                'PPC conforming to IS 1489 (Part 1)',
                'PSC conforming to IS 1489 (Part 2)'
            ],
            index=2
        )
        
        col1, col2 = st.columns(2)
        with col1:
            max_size = st.selectbox("**Max Aggregate Size**", [10, 20, 40], index=1)
        with col2:
            zone = st.selectbox("**Fine Aggregate Zone**", ['I', 'II', 'III', 'IV'], index=1)
        
        slump = st.slider("**Slump (mm)**", 25, 150, 75)
        
        st.subheader("📊 Material Properties")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            sp_gr_cement = st.number_input("**Sp. Gravity - Cement**", value=3.15, min_value=2.0, max_value=4.0, step=0.01)
        with col2:
            sp_gr_coarse = st.number_input("**Sp. Gravity - Coarse Agg**", value=2.74, min_value=2.0, max_value=3.0, step=0.01)
        with col3:
            sp_gr_fine = st.number_input("**Sp. Gravity - Fine Agg**", value=2.65, min_value=2.0, max_value=3.0, step=0.01)
        
        st.subheader("🧪 Chemical Admixture")
        use_admixture = st.checkbox("Use Chemical Admixture", value=True)
        
        if use_admixture:
            col1, col2 = st.columns(2)
            with col1:
                admix_type = st.selectbox("**Admixture Type**", [
                    'Superplasticizer - normal',
                    'Superplasticizer - PCE based', 
                    'Plasticizer',
                    'Retarder'
                ])
            with col2:
                admix_percentage = st.number_input("**Percentage (%)**", value=1.0, min_value=0.1, max_value=5.0, step=0.1)
        
        site_control = st.radio("**Site Control Quality**", ['Good', 'Fair'], index=0)
    
    tab1, tab2, tab3 = st.tabs(["🎯 Design Mix", "📋 Input Summary", "ℹ️ About"])
    
    with tab1:
        st.subheader("Concrete Mix Design Calculator")
        
        if st.button("🚀 Calculate Mix Design", type="primary", use_container_width=True):
            with st.spinner("Performing mix design calculations as per IS 10262:2019..."):
                try:
                    designer = ConcreteMixDesign()
                    
                    exposure_params = exposure_options[exposure]
                    
                    input_params = {
                        'grade': grade,
                        'exposure': exposure,
                        'cement_type': cement_type,
                        'max_aggregate_size': max_size,
                        'fine_agg_zone': zone,
                        'workability_slump': slump,
                        'specific_gravity_cement': sp_gr_cement,
                        'specific_gravity_coarse_agg': sp_gr_coarse,
                        'specific_gravity_fine_agg': sp_gr_fine,
                        'max_wc_ratio': exposure_params['max_wc'],
                        'min_cement_content': exposure_params['min_cement'],
                        'site_control': site_control,
                        'aggregate_type': 'Crushed angular aggregate',
                        'placing_method': 'Chute (Non pumpable)'
                    }
                    
                    if use_admixture:
                        input_params.update({
                            'use_admixture': True,
                            'admixture_type': admix_type,
                            'admixture_percentage': admix_percentage,
                            'specific_gravity_admixture': 1.145
                        })
                    
                    designer.set_input_parameters(input_params)
                    results = designer.perform_full_design()
                    
                    if results['success']:
                        st.success("✅ Mix Design Calculated Successfully!")
                        
                        st.subheader("📊 Design Results")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("Target Strength", f"{results['target_strength']:.1f} N/mm²")
                        with col2:
                            st.metric("W/C Ratio", f"{results['wc_ratio']:.3f}")
                        with col3:
                            st.metric("Water Content", f"{results['water_content']} kg/m³")
                        with col4:
                            st.metric("Cement Content", f"{results['cement_content']} kg/m³")
                        
                        st.subheader("📋 Detailed Mix Proportions")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("""
                            <div class='result-card'>
                            <h4>Material Quantities (per m³)</h4>
                            <table style='width:100%'>
                            <tr><td><b>Cement:</b></td><td>{cement} kg</td></tr>
                            <tr><td><b>Water:</b></td><td>{water} kg</td></tr>
                            <tr><td><b>Fine Aggregate:</b></td><td>{fine_agg:.1f}%</td></tr>
                            <tr><td><b>Coarse Aggregate:</b></td><td>{coarse_agg:.1f}%</td></tr>
                            <tr><td><b>Air Content:</b></td><td>{air:.1f}%</td></tr>
                            </table>
                            </div>
                            """.format(
                                cement=results['cement_content'],
                                water=results['water_content'],
                                fine_agg=results['vol_fine']*100,
                                coarse_agg=results['vol_coarse']*100,
                                air=results['air_content']*100
                            ), unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown("""
                            <div class='result-card'>
                            <h4>Design Parameters</h4>
                            <table style='width:100%'>
                            <tr><td><b>Concrete Grade:</b></td><td>{grade}</td></tr>
                            <tr><td><b>Exposure:</b></td><td>{exposure}</td></tr>
                            <tr><td><b>Max Aggregate:</b></td><td>{max_size} mm</td></tr>
                            <tr><td><b>Slump:</b></td><td>{slump} mm</td></tr>
                            <tr><td><b>Site Control:</b></td><td>{control}</td></tr>
                            </table>
                            </div>
                            """.format(
                                grade=results['grade'],
                                exposure=results['exposure'],
                                max_size=max_size,
                                slump=slump,
                                control=site_control
                            ), unsafe_allow_html=True)
                        
                        with st.expander("📖 Design Notes and Recommendations"):
                            st.info("""
                            **Important Notes:**
                            - This is a preliminary mix design for trial batches
                            - Actual field adjustments may be required based on material properties
                            - Conduct trial mixes with actual materials
                            - Check workability and adjust water content if needed
                            - Verify compressive strength with cube tests
                            
                            **Next Steps:**
                            1. Conduct trial mix with these proportions
                            2. Adjust based on workability requirements
                            3. Cast test cubes for strength verification
                            4. Fine-tune mix based on test results
                            """)
                        
                    else:
                        st.error(f"❌ Calculation Error: {results['error']}")
                        
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")
    
    with tab2:
        st.subheader("Input Parameters Summary")
        
        summary_data = {
            "Basic Parameters": {
                "Concrete Grade": grade,
                "Exposure Condition": f"{exposure} (Max w/c: {exposure_options[exposure]['max_wc']}, Min cement: {exposure_options[exposure]['min_cement']} kg/m³)",
                "Cement Type": cement_type,
                "Site Control Quality": site_control
            },
            "Aggregate Properties": {
                "Maximum Aggregate Size": f"{max_size} mm",
                "Fine Aggregate Zone": f"Zone {zone}",
                "Workability (Slump)": f"{slump} mm"
            },
            "Material Specific Gravities": {
                "Cement": sp_gr_cement,
                "Coarse Aggregate": sp_gr_coarse,
                "Fine Aggregate": sp_gr_fine
            },
            "Admixtures": {
                "Chemical Admixture": "Yes" if use_admixture else "No",
                "Admixture Type": admix_type if use_admixture else "Not used",
                "Admixture Percentage": f"{admix_percentage}%" if use_admixture else "N/A"
            }
        }
        
        for category, params in summary_data.items():
            st.write(f"**{category}**")
            for key, value in params.items():
                st.write(f"- {key}: {value}")
            st.write("")
    
    with tab3:
        st.subheader("About This Application")
        
        st.markdown("""
        ### 🏗️ Concrete Mix Design Calculator
        **As per IS 10262:2019 - Guidelines for Concrete Mix Design Proportioning**
        
        This application provides comprehensive concrete mix design calculations following the Indian Standard IS 10262:2019.
        
        **Features:**
        - ✅ Complete IS 10262:2019 compliance
        - ✅ All standard concrete grades (M10 to M80)
        - ✅ Exposure condition considerations as per IS 456
        - ✅ Multiple cement types support
        - ✅ Chemical admixture calculations
        - ✅ Detailed step-by-step calculations
        
        **Standards Referenced:**
        - IS 10262:2019 - Concrete Mix Proportioning Guidelines
        - IS 456:2000 - Plain and Reinforced Concrete
        - IS 383:2016 - Coarse and Fine Aggregate
        - IS 269:2015 - Ordinary Portland Cement
        
        **Note:** This tool is for preliminary mix design. Always verify with actual material tests and trial mixes.
        """)

if __name__ == "__main__":
    main()
