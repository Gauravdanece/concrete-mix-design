import streamlit as st
import math

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
                'target_strength': round(target_strength, 2),
                'wc_ratio': round(wc_ratio, 3),
                'water_content': water_content,
                'cement_content': cement_content,
                'vol_coarse': round(vol_coarse, 3),
                'vol_fine': round(vol_fine, 3),
                'air_content': round(air_content, 3),
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
        layout="wide"
    )
    
    st.title("🏗️ Concrete Mix Design Calculator")
    st.markdown("### As per IS 10262:2019 Standards")
    
    with st.sidebar:
        st.header("Design Parameters")
        
        grade = st.selectbox(
            "Concrete Grade",
            ['M15', 'M20', 'M25', 'M30', 'M35', 'M40'],
            index=2
        )
        
        exposure_options = {
            'Mild': {'max_wc': 0.55, 'min_cement': 220},
            'Moderate': {'max_wc': 0.50, 'min_cement': 240},
            'Severe': {'max_wc': 0.45, 'min_cement': 320},
            'Very Severe': {'max_wc': 0.40, 'min_cement': 340},
            'Extreme': {'max_wc': 0.35, 'min_cement': 360}
        }
        
        exposure = st.selectbox(
            "Exposure Condition",
            list(exposure_options.keys()),
            index=2
        )
        
        cement_type = st.selectbox(
            "Cement Type",
            [
                'OPC 33 Grade',
                'OPC 43 Grade',
                'OPC 53 Grade',
                'PPC',
                'PSC'
            ],
            index=2
        )
        
        col1, col2 = st.columns(2)
        with col1:
            max_size = st.selectbox("Max Aggregate Size (mm)", [10, 20, 40], index=1)
        with col2:
            zone = st.selectbox("Fine Aggregate Zone", ['I', 'II', 'III', 'IV'], index=1)
        
        slump = st.slider("Slump (mm)", 25, 150, 75)
        
        st.subheader("Material Properties")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            sp_gr_cement = st.number_input("Sp. Gravity - Cement", value=3.15, min_value=2.0, max_value=4.0, step=0.01)
        with col2:
            sp_gr_coarse = st.number_input("Sp. Gravity - Coarse Agg", value=2.74, min_value=2.0, max_value=3.0, step=0.01)
        with col3:
            sp_gr_fine = st.number_input("Sp. Gravity - Fine Agg", value=2.65, min_value=2.0, max_value=3.0, step=0.01)
        
        use_admixture = st.checkbox("Use Chemical Admixture", value=False)
        
        site_control = st.radio("Site Control Quality", ['Good', 'Fair'], index=0)
    
    if st.button("Calculate Mix Design", type="primary"):
        with st.spinner("Calculating..."):
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
                    'placing_method': 'Chute (Non pumpable)',
                    'use_admixture': use_admixture
                }
                
                if use_admixture:
                    input_params.update({
                        'admixture_type': 'Superplasticizer - normal',
                        'admixture_percentage': 1.0,
                        'specific_gravity_admixture': 1.145
                    })
                
                designer.set_input_parameters(input_params)
                results = designer.perform_full_design()
                
                if results['success']:
                    st.success("✅ Mix Design Calculated Successfully!")
                    
                    st.subheader("Design Results")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Target Strength", f"{results['target_strength']} N/mm²")
                    with col2:
                        st.metric("W/C Ratio", f"{results['wc_ratio']}")
                    with col3:
                        st.metric("Water Content", f"{results['water_content']} kg/m³")
                    with col4:
                        st.metric("Cement Content", f"{results['cement_content']} kg/m³")
                    
                    st.subheader("Mix Proportions")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Material Quantities (per m³)**")
                        st.write(f"- Cement: {results['cement_content']} kg")
                        st.write(f"- Water: {results['water_content']} kg")
                        st.write(f"- Fine Aggregate: {results['vol_fine']*100:.1f}%")
                        st.write(f"- Coarse Aggregate: {results['vol_coarse']*100:.1f}%")
                        st.write(f"- Air Content: {results['air_content']*100:.1f}%")
                    
                    with col2:
                        st.write("**Design Parameters**")
                        st.write(f"- Concrete Grade: {results['grade']}")
                        st.write(f"- Exposure: {results['exposure']}")
                        st.write(f"- Max Aggregate: {max_size} mm")
                        st.write(f"- Slump: {slump} mm")
                        st.write(f"- Site Control: {site_control}")
                    
                    st.info("""
                    **Note:** This is a preliminary mix design. 
                    Conduct trial mixes with actual materials and adjust as needed.
                    """)
                    
                else:
                    st.error(f"Error: {results['error']}")
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
