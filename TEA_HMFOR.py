import matplotlib.transforms as transforms
import matplotlib.pyplot as plt
import numpy as np
import pygal
import io
from matplotlib.figure import Figure
import io
from matplotlib.backends.backend_svg import FigureCanvasSVG

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

    return([NPV, payback_time, product_income, [electricity_operating, maintenance_operating,
                                                crystal_operating, water_operating, hmf_operating], [electrolyzer_captital, crystal_captital, plant_capital]])


def HMFOR_plots(HMFOR_inputs, cd_lower, cd_upper, cv_lower, cv_upper, FE_lower, FE_upper, yield_lower, yield_upper):
    # Generates plots for HMFOR reaction

    [NPV_base, payback_time_base, product_income, op_costs,
        cap_costs] = HMFOR_TEA(*HMFOR_inputs)

    # ________Pie Charts__________

    # Operating Costs
    op_cost_pie = pygal.Pie()
    op_cost_pie.title = 'Annual Operating Cost Breakdown ($)'
    op_cost_pie.add('Electricity', round(op_costs[0], 2))
    op_cost_pie.add('Maintenance', round(op_costs[1], 2))
    op_cost_pie.add('Crystallization', round(op_costs[2], 2))
    op_cost_pie.add('Water', round(op_costs[3], 2))
    op_cost_pie.add('HMF input', round(op_costs[4], 2))

    op_cost_pie_data = op_cost_pie.render_data_uri()

    # Operating Costs without HMF
    op_cost_pie_no_hmf = pygal.Pie()
    op_cost_pie_no_hmf.title = 'Annual Operating Cost Breakdown Excluding HMF ($)'
    op_cost_pie_no_hmf.add('Electricity', round(op_costs[0], 2))
    op_cost_pie_no_hmf.add('Maintenance', round(op_costs[1], 2))
    op_cost_pie_no_hmf.add('Crystallization', round(op_costs[2], 2))
    op_cost_pie_no_hmf.add('Water', round(op_costs[3], 2))

    op_cost_pie_no_hmf_data = op_cost_pie_no_hmf.render_data_uri()

    # Capital Costs
    cap_cost_pie = pygal.Pie()
    cap_cost_pie.title = 'Capital Cost Breakdown ($)'
    cap_cost_pie.add('Electrolyzer', round(cap_costs[0], 2))
    cap_cost_pie.add('Crystallizer', round(cap_costs[1], 2))
    cap_cost_pie.add('Balance', round(cap_costs[2], 2))

    cap_cost_pie_data = cap_cost_pie.render_data_uri()

    # ________Sensitivity Analysis Charts__________

    # Set up scenarios (+/- 10%)

    sa_vars = ['Electrolyzer Cost', 'Faradaic Efficiency', 'FDCA Yield',
               'Cell Voltage', 'Current Density', 'HMF Price', 'Electricity Price']

    sa_lower_vars = [[0.9*HMFOR_inputs[7], HMFOR_inputs[13], HMFOR_inputs[14], HMFOR_inputs[12],
                      HMFOR_inputs[11], HMFOR_inputs[6], HMFOR_inputs[3]],

                     [HMFOR_inputs[7], 0.9*HMFOR_inputs[13], HMFOR_inputs[14], HMFOR_inputs[12],
                      HMFOR_inputs[11], HMFOR_inputs[6], HMFOR_inputs[3]],

                     [HMFOR_inputs[7], HMFOR_inputs[13], 0.9*HMFOR_inputs[14], HMFOR_inputs[12],
                      HMFOR_inputs[11], HMFOR_inputs[6], HMFOR_inputs[3]],

                     [HMFOR_inputs[7], HMFOR_inputs[13], HMFOR_inputs[14], 0.9*HMFOR_inputs[12],
                      HMFOR_inputs[11], HMFOR_inputs[6], HMFOR_inputs[3]],

                     [HMFOR_inputs[7], HMFOR_inputs[13], HMFOR_inputs[14], HMFOR_inputs[12],
                      0.9*HMFOR_inputs[11], HMFOR_inputs[6], HMFOR_inputs[3]],

                     [HMFOR_inputs[7], HMFOR_inputs[13], HMFOR_inputs[14], HMFOR_inputs[12],
                      HMFOR_inputs[11], 0.9*HMFOR_inputs[6], HMFOR_inputs[3]],

                     [HMFOR_inputs[7], HMFOR_inputs[13], HMFOR_inputs[14], HMFOR_inputs[12],
                      HMFOR_inputs[11], HMFOR_inputs[6], 0.9*HMFOR_inputs[3]],
                     ]

    sa_upper_vars = [[1.1*HMFOR_inputs[7], HMFOR_inputs[13], HMFOR_inputs[14], HMFOR_inputs[12],
                      HMFOR_inputs[11], HMFOR_inputs[6], HMFOR_inputs[3]],

                     [HMFOR_inputs[7], 1.1*HMFOR_inputs[13], HMFOR_inputs[14], HMFOR_inputs[12],
                      HMFOR_inputs[11], HMFOR_inputs[6], HMFOR_inputs[3]],

                     [HMFOR_inputs[7], HMFOR_inputs[13], 1.1*HMFOR_inputs[14], HMFOR_inputs[12],
                      HMFOR_inputs[11], HMFOR_inputs[6], HMFOR_inputs[3]],

                     [HMFOR_inputs[7], HMFOR_inputs[13], HMFOR_inputs[14], 1.1*HMFOR_inputs[12],
                      HMFOR_inputs[11], HMFOR_inputs[6], HMFOR_inputs[3]],

                     [HMFOR_inputs[7], HMFOR_inputs[13], HMFOR_inputs[14], HMFOR_inputs[12],
                      1.1*HMFOR_inputs[11], HMFOR_inputs[6], HMFOR_inputs[3]],

                     [HMFOR_inputs[7], HMFOR_inputs[13], HMFOR_inputs[14], HMFOR_inputs[12],
                      HMFOR_inputs[11], 1.1*HMFOR_inputs[6], HMFOR_inputs[3]],

                     [HMFOR_inputs[7], HMFOR_inputs[13], HMFOR_inputs[14], HMFOR_inputs[12],
                      HMFOR_inputs[11], HMFOR_inputs[6], 1.1*HMFOR_inputs[3]],
                     ]

    sa_lower = []
    for i in range(0, len(sa_lower_vars)):
        results = HMFOR_TEA(*HMFOR_inputs[:3], sa_lower_vars[i][6], *HMFOR_inputs[4:6], sa_lower_vars[i][5], sa_lower_vars[i][0],
                            *HMFOR_inputs[8:11], sa_lower_vars[i][4], sa_lower_vars[i][3], sa_lower_vars[i][1], sa_lower_vars[i][2], HMFOR_inputs[-1])
        sa_lower.append(results[0] / NPV_base-1)

    sa_upper = []
    for i in range(0, len(sa_upper_vars)):
        results = HMFOR_TEA(*HMFOR_inputs[:3], sa_upper_vars[i][6], *HMFOR_inputs[4:6], sa_upper_vars[i][5], sa_upper_vars[i][0],
                            *HMFOR_inputs[8:11], sa_upper_vars[i][4], sa_upper_vars[i][3], sa_upper_vars[i][1], sa_upper_vars[i][2], HMFOR_inputs[-1])
        sa_upper.append(results[0] / NPV_base-1)

    num_vars = len(sa_vars)

    # bars centered on the y axis
    pos = np.arange(num_vars) + .5

    # make the left and right axes
    fig = Figure()
    ax_lower = fig.add_axes([0.05, 0.1, 0.35, 0.8])
    ax_upper = fig.add_axes([0.6, 0.1, 0.35, 0.8])

    # just tick on the top
    ax_lower.xaxis.set_ticks_position('top')
    ax_upper.xaxis.set_ticks_position('top')

    # Set figure title
    fig.suptitle('Sensitivity Analysis')

    # set bar colors
    c_lower = []
    c_upper = []

    for i in range(0, num_vars):
        if sa_lower[i] < 0:
            c_lower.append('red')
        else:
            c_lower.append('green')

        if sa_upper[i] < 0:
            c_upper.append('red')
        else:
            c_upper.append('green')

    # make the lower graph
    ax_lower.barh(pos, [abs(ele) for ele in sa_lower], align='center', color=c_lower,
                  height=0.5, edgecolor='None')
    ax_lower.set_yticks([])
    ax_lower.invert_xaxis()

    # make the upper graph
    ax_upper.barh(pos, [abs(ele) for ele in sa_upper], align='center', color=c_upper,
                  height=0.5, edgecolor='None')
    ax_upper.set_yticks([])

    # we want the labels to be centered in the fig coord system and
    # centered w/ respect to the bars so we use a custom transform
    transform = transforms.blended_transform_factory(
        fig.transFigure, ax_upper.transData)
    for i, label in enumerate(sa_vars):
        ax_upper.text(0.5, i+0.5, label, ha='center', va='center',
                      transform=transform)

    # the axes titles are in axes coords, so x=0, y=1.025 is on the left
    # side of the axes, just above, x=1.0, y=1.025 is the right side of the
    # axes, just above
    ax_upper.set_title('+10%', x=-0.15, y=0.97, fontsize=12)
    ax_lower.set_title('-10%', x=1.15, y=0.97, fontsize=12)

    # adding the annotations
    for i in range(0, num_vars):
        ax_upper.annotate(str(round(abs(sa_upper[i])*100, 2)) + '%', xy=(0.00001, 0.5 + i),
                          xycoords='data',
                          xytext=(16, 0), textcoords='offset points',
                          size=10,
                          va='center')
        ax_lower.annotate(str(round(abs(sa_lower[i])*100, 2)) + '%', xy=(max([abs(ele) for ele in sa_lower])/2, 0.5 + i),
                          xycoords='data',
                          xytext=(16, 0), textcoords='offset points',
                          size=10,
                          va='center')

    SA_output = io.BytesIO()
    FigureCanvasSVG(fig).print_svg(SA_output)

    # ________Color Scatter Charts__________

    scatter_step = 200

    # Current Density (x) vs Voltage (y)

    x = []
    y = []
    cd_cv_npv = []
    cd = cd_lower
    cv = cv_lower
    cd_step = (cd_upper-cd_lower)/scatter_step
    cv_step = (cv_upper-cv_lower)/scatter_step

    for i in range(0, scatter_step):
        for j in range(0, scatter_step):
            x.append(cd)
            y.append(cv)
            results = HMFOR_TEA(*HMFOR_inputs[:11], cd, cv, *HMFOR_inputs[13:])
            cd_cv_npv.append(results[0])
            cv += cv_step
        cd += cd_step
        cv = cv_lower

    fig = Figure()

    ax = fig.add_subplot(111)
    im = ax.scatter(x, y, s=3, c=cd_cv_npv)
    ax.scatter(HMFOR_inputs[11], HMFOR_inputs[12],
               edgecolors='black', s=8, c='b')
    ax.set_xlabel('Current Density $[A/cm^2]$')
    ax.set_ylabel('Cell Voltage $[V]$')
    ax.set_title('Current Density vs Cell Voltage')
    ax.set_xlim(cd_lower, cd_upper)
    ax.set_ylim(cv_lower, cv_upper)
    ax.set_xticks(np.arange(cd_lower, cd_upper +
                            10 ** -8, (cd_upper-cd_lower)/4))
    ax.set_yticks(np.arange(cv_lower, cv_upper +
                            10 ** -8, (cv_upper-cv_lower)/4))

    fig.colorbar(im, ax=ax, label='Net Present Value [$]')

    cd_cv_output = io.BytesIO()
    FigureCanvasSVG(fig).print_svg(cd_cv_output)

    # FE (x) vs Voltage (y)

    x = []
    y = []
    fe_cv_npv = []
    FE = FE_lower
    cv = cv_lower
    FE_step = (FE_upper-FE_lower)/scatter_step
    cv_step = (cv_upper-cv_lower)/scatter_step

    for i in range(0, scatter_step):
        for j in range(0, scatter_step):
            x.append(FE)
            y.append(cv)
            results = HMFOR_TEA(*HMFOR_inputs[:12], cv, FE, *HMFOR_inputs[14:])
            fe_cv_npv.append(results[0])
            cv += cv_step
        FE += FE_step
        cv = cv_lower

    fig = Figure()
    # fig = plt.figure()

    ax = fig.add_subplot(111)
    im = ax.scatter(x, y, s=3, c=fe_cv_npv)
    ax.scatter(HMFOR_inputs[13], HMFOR_inputs[12],
               edgecolors='black', s=8, c='b')
    ax.set_xlabel('Faradaic Efficiency')
    ax.set_ylabel('Cell Voltage $[V]$')
    ax.set_title('Faradaic Efficienct vs Cell Voltage')
    ax.set_xlim(FE_lower, FE_upper)
    ax.set_ylim(cv_lower, cv_upper)
    ax.set_xticks(np.arange(FE_lower, FE_upper +
                            10 ** -8, (FE_upper-FE_lower)/4))
    ax.set_yticks(np.arange(cv_lower, cv_upper +
                            10 ** -8, (cv_upper-cv_lower)/4))

    fig.colorbar(im, ax=ax, label='Net Present Value [$]')

    fe_cv_output = io.BytesIO()
    FigureCanvasSVG(fig).print_svg(fe_cv_output)

    """
    # Yield (x) vs Voltage (y)

    x = []
    y = []
    yld_cv_npv = []
    yld = yield_lower
    cv = cv_lower
    yld_step = (yield_upper-yield_lower)/scatter_step
    cv_step = (cv_upper-cv_lower)/scatter_step

    for i in range(0, scatter_step):
        for j in range(0, scatter_step):
            x.append(yld)
            y.append(cv)
            results = HMFOR_TEA(
                *HMFOR_inputs[:12], cv, HMFOR_inputs[13], yld, HMFOR_inputs[-1])
            yld_cv_npv.append(results[0])
            cv += cv_step
        yld += yld_step
        cv = cv_lower

    plt.scatter(x, y, edgecolors='none', s=3, c=yld_cv_npv)
    plt.colorbar(label='Net Present Value [$]')
    plt.scatter(HMFOR_inputs[14], HMFOR_inputs[12],
                edgecolors='black', s=8, c='b')
    plt.title('FDCA Yield vs Cell Voltage')
    plt.xlabel('FDCA Yield')
    plt.ylabel('Cell Voltage [V]')
    plt.xlim(yield_lower, yield_upper)
    plt.xticks(np.arange(yield_lower, yield_upper +
                         10 ** -8, (yield_lower-yield_upper)/4))
    plt.ylim(cv_lower, cv_upper)
    plt.yticks(np.arange(cv_lower, cv_upper + 10 ** -8, (cv_upper-cv_lower)/4))
    plt.show()

    # Current Density vs NPV

    x = []
    y = []
    cd = cd_lower
    cd_step = (cd_upper-cd_lower)/scatter_step

    for i in range(0, scatter_step):
        x.append(cd)
        results = HMFOR_TEA(*HMFOR_inputs[:11], cd, cv, *HMFOR_inputs[13:])
        y.append(results[0])
        cd += cd_step

    plt.plot(x, y)
    plt.title('Current Density vs NPV')
    plt.xlabel('Current Density [A/cm^2]')
    plt.ylabel('Net Present Value [$]')
    plt.show()

    return([NPV_base, payback_time_base])
    """
    # return [op_cost_pie_data, op_cost_pie_no_hmf_data, cap_cost_pie_data, figdata_svg]
    return [op_cost_pie_data, op_cost_pie_no_hmf_data, cap_cost_pie_data, SA_output, cd_cv_output, fe_cv_output]


HMFOR_inputs = [product_production, product_price, operating_time,
                electricity_price, h2_price, water_price, hmf_price,
                electrolyzer_reference_cost, income_tax, interest_rate, plant_lifetime,
                current_density, cell_voltage, faradaic_efficiency, fdca_yield, electrolyte_density]

# print(HMFOR_TEA(*HMFOR_inputs))

HMFOR_plots(HMFOR_inputs, 0.02, 0.06, 1, 2, 0.8, 1, 0.8, 1)
