from TEA_HMFOR import HMFOR_TEA, HMFOR_inputs, HMFOR_plots
from flask import Flask, jsonify, render_template, Response
import os
import sys
import pygal
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import io
from matplotlib.backends.backend_svg import FigureCanvasSVG
import matplotlib.transforms as transforms
import numpy as np


print(sys.executable)

app = Flask(__name__)


@app.route('/')
def hello_world():
    return jsonify({"about": 'Hello, World!'})


@app.route('/HMFOR/production=<float:prod>/fdca_p=<float:prod_price>/t_op=<float:op_time>/elec_p=<float:elec_p>/h2_p=<float:h2_p>/h2o_p=<float:h2o_p>/hmf_p=<float:hmf_p>/elec_ref=<float:elec_ref>/t=<float:t>/r=<float:r>/plant_life=<float:plant_life>/cur_den=<float:cur_den>/cell_v=<float:cell_v>/FE=<float:FE>/fdca_y=<float:fdca_y>/elec_den=<float:elec_den>', methods=['GET'])
def hmfor(prod, prod_price, op_time,
          elec_p, h2_p, h2o_p, hmf_p,
          elec_ref, t, r, plant_life,
          cur_den, cell_v, FE, fdca_y, elec_den):
    HMFOR_inputs = [prod, prod_price, op_time,
                    elec_p, h2_p, h2o_p, hmf_p,
                    elec_ref, t, r, plant_life,
                    cur_den, cell_v, FE, fdca_y, elec_den]
    [NPV, payback_time, product_income, op_costs,
        cap_costs] = HMFOR_TEA(*HMFOR_inputs)
    return jsonify({"NPV": NPV, "payback_time": payback_time})


@app.route('/hmfor_plots')
def hmfor_plots():

    [op_cost, op_cost_no_hmf, cap_cost, SA_output, cd_cv_output] = HMFOR_plots(
        HMFOR_inputs, 0.02, 0.06, 1, 2, 0.8, 1, 0.8, 1)

    return Response(cd_cv_output.getvalue(), mimetype="image/svg+xml")

    # return render_template('charts.html', op_cost=op_cost, op_cost_no_hmf=op_cost_no_hmf, cap_cost=cap_cost)
    # return render_template('charts.html', op_cost=op_cost, op_cost_no_hmf=op_cost_no_hmf, cap_cost=cap_cost, sen_ana=sen_ana)


@app.route('/matplot')
def plot_svg(num_x_points=50):
    """ renders the plot on the fly.
    """
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    x_points = range(num_x_points)
    axis.plot(x_points, range(num_x_points))

    output = io.BytesIO()
    FigureCanvasSVG(fig).print_svg(output)
    return Response(output.getvalue(), mimetype="image/svg+xml")


# @app.route('/saplot')
# def plot_sa():
#     """ renders the plot on the fly.
#     """
#     [NPV_base, payback_time_base, product_income, op_costs,
#         cap_costs] = HMFOR_TEA(*HMFOR_inputs)

#     # ________Sensitivity Analysis Charts__________

#     # Set up scenarios (+/- 10%)

#     sa_vars = ['Electrolyzer Cost', 'Faradaic Efficiency', 'FDCA Yield',
#                'Cell Voltage', 'Current Density', 'HMF Price', 'Electricity Price']

#     sa_lower_vars = [[0.9*HMFOR_inputs[7], HMFOR_inputs[13], HMFOR_inputs[14], HMFOR_inputs[12],
#                       HMFOR_inputs[11], HMFOR_inputs[6], HMFOR_inputs[3]],

#                      [HMFOR_inputs[7], 0.9*HMFOR_inputs[13], HMFOR_inputs[14], HMFOR_inputs[12],
#                       HMFOR_inputs[11], HMFOR_inputs[6], HMFOR_inputs[3]],

#                      [HMFOR_inputs[7], HMFOR_inputs[13], 0.9*HMFOR_inputs[14], HMFOR_inputs[12],
#                       HMFOR_inputs[11], HMFOR_inputs[6], HMFOR_inputs[3]],

#                      [HMFOR_inputs[7], HMFOR_inputs[13], HMFOR_inputs[14], 0.9*HMFOR_inputs[12],
#                       HMFOR_inputs[11], HMFOR_inputs[6], HMFOR_inputs[3]],

#                      [HMFOR_inputs[7], HMFOR_inputs[13], HMFOR_inputs[14], HMFOR_inputs[12],
#                       0.9*HMFOR_inputs[11], HMFOR_inputs[6], HMFOR_inputs[3]],

#                      [HMFOR_inputs[7], HMFOR_inputs[13], HMFOR_inputs[14], HMFOR_inputs[12],
#                       HMFOR_inputs[11], 0.9*HMFOR_inputs[6], HMFOR_inputs[3]],

#                      [HMFOR_inputs[7], HMFOR_inputs[13], HMFOR_inputs[14], HMFOR_inputs[12],
#                       HMFOR_inputs[11], HMFOR_inputs[6], 0.9*HMFOR_inputs[3]],
#                      ]

#     sa_upper_vars = [[1.1*HMFOR_inputs[7], HMFOR_inputs[13], HMFOR_inputs[14], HMFOR_inputs[12],
#                       HMFOR_inputs[11], HMFOR_inputs[6], HMFOR_inputs[3]],

#                      [HMFOR_inputs[7], 1.1*HMFOR_inputs[13], HMFOR_inputs[14], HMFOR_inputs[12],
#                       HMFOR_inputs[11], HMFOR_inputs[6], HMFOR_inputs[3]],

#                      [HMFOR_inputs[7], HMFOR_inputs[13], 1.1*HMFOR_inputs[14], HMFOR_inputs[12],
#                       HMFOR_inputs[11], HMFOR_inputs[6], HMFOR_inputs[3]],

#                      [HMFOR_inputs[7], HMFOR_inputs[13], HMFOR_inputs[14], 1.1*HMFOR_inputs[12],
#                       HMFOR_inputs[11], HMFOR_inputs[6], HMFOR_inputs[3]],

#                      [HMFOR_inputs[7], HMFOR_inputs[13], HMFOR_inputs[14], HMFOR_inputs[12],
#                       1.1*HMFOR_inputs[11], HMFOR_inputs[6], HMFOR_inputs[3]],

#                      [HMFOR_inputs[7], HMFOR_inputs[13], HMFOR_inputs[14], HMFOR_inputs[12],
#                       HMFOR_inputs[11], 1.1*HMFOR_inputs[6], HMFOR_inputs[3]],

#                      [HMFOR_inputs[7], HMFOR_inputs[13], HMFOR_inputs[14], HMFOR_inputs[12],
#                       HMFOR_inputs[11], HMFOR_inputs[6], 1.1*HMFOR_inputs[3]],
#                      ]

#     sa_lower = []
#     for i in range(0, len(sa_lower_vars)):
#         results = HMFOR_TEA(*HMFOR_inputs[:3], sa_lower_vars[i][6], *HMFOR_inputs[4:6], sa_lower_vars[i][5], sa_lower_vars[i][0],
#                             *HMFOR_inputs[8:11], sa_lower_vars[i][4], sa_lower_vars[i][3], sa_lower_vars[i][1], sa_lower_vars[i][2], HMFOR_inputs[-1])
#         sa_lower.append(results[0] / NPV_base-1)

#     sa_upper = []
#     for i in range(0, len(sa_upper_vars)):
#         results = HMFOR_TEA(*HMFOR_inputs[:3], sa_upper_vars[i][6], *HMFOR_inputs[4:6], sa_upper_vars[i][5], sa_upper_vars[i][0],
#                             *HMFOR_inputs[8:11], sa_upper_vars[i][4], sa_upper_vars[i][3], sa_upper_vars[i][1], sa_upper_vars[i][2], HMFOR_inputs[-1])
#         sa_upper.append(results[0] / NPV_base-1)

#     num_vars = len(sa_vars)

#     # bars centered on the y axis
#     pos = np.arange(num_vars) + .5

#     # make the left and right axes
#     fig = Figure()
#     ax_lower = fig.add_axes([0.05, 0.1, 0.35, 0.8])
#     ax_upper = fig.add_axes([0.6, 0.1, 0.35, 0.8])

#     # step_lower = max([abs(ele) for ele in sa_lower])/4
#     # step_upper = max([abs(ele) for ele in sa_upper])/4

#     # ax_upper.set_xticks(np.arange(0.05, 4*step_upper, step_upper))
#     # ax_lower.set_xticks(np.arange(0.05, 4*step_lower, step_lower))

#     # just tick on the top
#     ax_lower.xaxis.set_ticks_position('top')
#     ax_upper.xaxis.set_ticks_position('top')

#     # Set figure title
#     fig.suptitle('Sensitivity Analysis')

#     # set bar colors
#     c_lower = []
#     c_upper = []

#     for i in range(0, num_vars):
#         if sa_lower[i] < 0:
#             c_lower.append('red')
#         else:
#             c_lower.append('green')

#         if sa_upper[i] < 0:
#             c_upper.append('red')
#         else:
#             c_upper.append('green')

#     # make the lower graph
#     ax_lower.barh(pos, [abs(ele) for ele in sa_lower], align='center', color=c_lower,
#                   height=0.5, edgecolor='None')
#     ax_lower.set_yticks([])
#     ax_lower.invert_xaxis()

#     # make the upper graph
#     ax_upper.barh(pos, [abs(ele) for ele in sa_upper], align='center', color=c_upper,
#                   height=0.5, edgecolor='None')
#     ax_upper.set_yticks([])

#     # we want the labels to be centered in the fig coord system and
#     # centered w/ respect to the bars so we use a custom transform
#     transform = transforms.blended_transform_factory(
#         fig.transFigure, ax_upper.transData)
#     for i, label in enumerate(sa_vars):
#         ax_upper.text(0.5, i+0.5, label, ha='center', va='center',
#                       transform=transform)

#     # the axes titles are in axes coords, so x=0, y=1.025 is on the left
#     # side of the axes, just above, x=1.0, y=1.025 is the right side of the
#     # axes, just above
#     ax_upper.set_title('+10%', x=-0.15, y=0.97, fontsize=12)
#     ax_lower.set_title('-10%', x=1.15, y=0.97, fontsize=12)

#     # adding the annotations
#     for i in range(0, num_vars):
#         ax_upper.annotate(str(round(abs(sa_upper[i])*100, 2)) + '%', xy=(0.00001, 0.5 + i),
#                           xycoords='data',
#                           xytext=(16, 0), textcoords='offset points',
#                           size=10,
#                           va='center')
#         ax_lower.annotate(str(round(abs(sa_lower[i])*100, 2)) + '%', xy=(max([abs(ele) for ele in sa_lower])/2, 0.5 + i),
#                           xycoords='data',
#                           xytext=(16, 0), textcoords='offset points',
#                           size=10,
#                           va='center')

#     SA_output = io.BytesIO()
#     FigureCanvasSVG(fig).print_svg(SA_output)

#     return Response(SA_output.getvalue(), mimetype="image/svg+xml")

# @app.route('/pygal/')
# def pygal_example():
#     chart = pygal.Pie()
#     chart.title = 'Browser usage in February 2012 (in %)'
#     chart.add('IE', 19.5)
#     chart.add('Firefox', 36.6)
#     chart.add('Chrome', 36.3)
#     chart.add('Safari', 4.5)
#     chart.add('Opera', 2.3)

#     chart_data1 = chart.render_data_uri()

#     line_chart = pygal.Line()
#     line_chart.title = 'Browser usage evolution (in %)'
#     line_chart.x_labels = map(str, range(2002, 2013))
#     line_chart.add('Firefox', [None, None,    0, 16.6,
#                                25,   31, 36.4, 45.5, 46.3, 42.8, 37.1])
#     line_chart.add('Chrome',  [None, None, None, None,
#                                None, None,    0,  3.9, 10.8, 23.8, 35.3])
#     line_chart.add('IE',      [85.8, 84.6, 84.7, 74.5,
#                                66, 58.6, 54.7, 44.8, 36.2, 26.6, 20.1])
#     line_chart.add('Others',  [14.2, 15.4, 15.3,  8.9,
#                                9, 10.4,  8.9,  5.8,  6.7,  6.8,  7.5])

#     chart_data2 = line_chart.render_data_uri()

#     return render_template('charts.html', chart_data1=chart_data1, chart_data2=chart_data2)

if __name__ == '__main__':
    app.run(debug=True)

# print(HMFOR_TEA(prod, prod_price, op_time,
#             elec_p, h2_p, h2o_p, hmf_p,
#             elec_ref, t, r, plant_life,
#             cur_den, cell_v, FE, fdca_y, elec_den))
