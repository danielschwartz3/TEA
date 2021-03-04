import matplotlib
# matplotlib.use('TkAgg')
# import matplotlib.pyplot as plt

import numpy as np

# _______________________ Inputs _________________________
# Economic Parameters
product_production = 100000         # [kg/day]
product_price = 1445                # [$/ton]
operating_time = 350                # [days/year]
electricity_price = 0.02            # [$/kWh]
h2_price = 1.5                      # [$/kg]
water_price = 0.0054/3.79           # [$/kg]
hmf_price = 0.9095                  # [$/kg]
electrolyzer_reference_cost = 920   # [$/m^2]
income_tax = 0.389
interest_rate = 0.1                 # Nominal
plant_lifetime = 20                 # [years]

# Lab Parameters
current_density = 0.05              # [A/cm^2]
cell_voltage = 1.4                  # [V]
faradaic_efficiency = 1
fdca_yield = 0.98
electrolyte_density = 2.13          # [kg/L]

# # Constants
# product_MW = 156.093                # [g/mol]
# product_density = 1.6               # [kg/L]
# hmf_MW = 126.110                    # [g/mol]
# electrons_per_molecule = 6

# # Crystallization Parameters
# crystal_capcity_scale_factor = 0.7
# crystal_reference_cost = 159000  # [$]
# crystal_reference_capacity = 1427000.00  # [kg/day]
# crystal_reference_power = (7.1 * 1000) / (1427000 / 24)  # [kWh/kg]

# # Depreciation
# dep = [0.10, 0.18, 0.144, 0.1152, 0.0922, 0.0737,
#        0.0655, 0.0655, 0.0656, 0.0655, 0.0328]

# _______________________ Calculations _________________________


def HMFOR_TEA(product_production: float, product_price: float, operating_time: float,
              electricity_price: float, h2_price: float, water_price: float, hmf_price: float,
              electrolyzer_reference_cost: float, income_tax: float, interest_rate: float, plant_lifetime: float,
              current_density: float, cell_voltage: float, faradaic_efficiency: float, fdca_yield: float, electrolyte_density: float):
    # This function calculates the TEA for the HMF OR reaction

    # Constants
    product_MW = 156.093                # [g/mol]
    product_density = 1.6               # [kg/L]
    hmf_MW = 126.110                    # [g/mol]
    electrons_per_molecule = 6

    # Crystallization Parameters
    crystal_capcity_scale_factor = 0.7
    crystal_reference_cost = 159000  # [$]
    crystal_reference_capacity = 1427000.00  # [kg/day]
    crystal_reference_power = (7.1 * 1000) / (1427000 / 24)  # [kWh/kg]

    # Depreciation
    dep = [0.10, 0.18, 0.144, 0.1152, 0.0922, 0.0737,
           0.0655, 0.0655, 0.0656, 0.0655, 0.0328]

    # Electrolyzer Banalnce
    current_needed = (product_production / 86400) * (1000 / product_MW) * \
        electrons_per_molecule * 96485 / faradaic_efficiency           # [A]
    electrolyzer_area = current_needed / (current_density * 10 ** 4)    # [m^2]
    power_needed = current_needed * cell_voltage / (10 ** 6)
    hmf_needed = (current_needed * faradaic_efficiency * hmf_MW *      # [MW]
                  86400 / (electrons_per_molecule * 96485*1000)) / (fdca_yield)     # [kd/day]

    electrolyte_flow_rate = (
        (product_production / product_density) / 0.1) * electrolyte_density  # [kg/day]
    o2_flow_rate = current_needed * 3/2 * \
        (1-faradaic_efficiency) / (6 * 96485) * \
        0.016 * 86400          # [kg/day]
    h2_flow_rate = current_needed * faradaic_efficiency * 3 / 6 / 96485 * 0.002 * 86400
    h2o_inlet_flow_rate = current_needed * \
        faradaic_efficiency * 6 / 6 / 96485 * \
        0.018 * 86400            # [kg/day]
    h2o_outlet_flow_rate = current_needed * \
        faradaic_efficiency * 4 / 6 / 96485 * \
        0.018 * 86400            # [kg/day]

    total_liquid_flow_rate = product_production + \
        electrolyte_flow_rate + \
        h2o_outlet_flow_rate                    # [kg/day]

    fdca_weight_fraction = product_production / total_liquid_flow_rate
    h2o_electrolyzer_area = current_needed / (2 * 10 ** 4)

    # Captial Costs

    electrolyzer_captital = electrolyzer_reference_cost * \
        (electrolyzer_area + h2o_electrolyzer_area)  # [$]

    crystal_captital = crystal_reference_cost * \
        (total_liquid_flow_rate /
         crystal_reference_capacity) ** crystal_capcity_scale_factor  # [$]

    plant_capital = (electrolyzer_captital +
                     crystal_captital) * 0.45 / 0.55  # [$]

    total_capital = plant_capital + \
        electrolyzer_captital + crystal_captital  # [$]

    # Operating Costs
    electricity_operating = power_needed * \
        electricity_price * 1000 * 24    # [$/day]
    maintenance_operating = (
        crystal_captital + electrolyzer_captital) * 0.025 / operating_time  # [$/day]
    crystal_operating = total_liquid_flow_rate * \
        electricity_price * crystal_reference_power         # [$/day]
    hmf_operating = hmf_needed * hmf_price                  # [$/day]
    water_operating = water_price * h2o_inlet_flow_rate     # [$/day]
    total_operating = electricity_operating + maintenance_operating + \
        crystal_operating + hmf_operating + water_operating  # [$/day]

    # Income
    product_income = product_production * \
        product_price / 1000 + h2_flow_rate * h2_price      # [$/day]
    annual_profit = (product_income - total_operating) * operating_time

    payback_time = total_capital / annual_profit            # [years]

    # NPV Calculations
    NPV = -total_capital - 0.05 * total_capital
    discount_facor = 1

    for i in range(1, int(plant_lifetime) + 1):
        discount_facor = discount_facor / (1 + interest_rate)
        CF = annual_profit * (1-income_tax)
        if i <= len(dep):
            CF += dep[i-1] * total_capital * income_tax
        NPV += CF * discount_facor

    return([NPV, payback_time])


# print(HMFOR_TEA(product_production, product_price, operating_time,
#             electricity_price, h2_price, water_price, hmf_price,
#             electrolyzer_reference_cost, income_tax, interest_rate, plant_lifetime,
#             current_density, cell_voltage, faradaic_efficiency, fdca_yield, electrolyte_density))

# Pie Charts

# Operating Costs
# y = np.array([35, 25, 25, 15])
# mylabels = ["Apples", "Bananas", "Cherries", "Dates"]
# myexplode = [0.2, 0, 0, 0]

# plt.pie(y, labels=mylabels, explode=myexplode)
# plt.show()
