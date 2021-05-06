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

    [op_cost, op_cost_no_hmf, cap_cost, SA_output, cd_cv_output, fe_cv_output] = HMFOR_plots(
        HMFOR_inputs, 0.02, 0.06, 1, 2, 0.8, 1, 0.8, 1)

    return Response(fe_cv_output.getvalue(), mimetype="image/svg+xml")

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


if __name__ == '__main__':
    app.run(debug=True)

# print(HMFOR_TEA(prod, prod_price, op_time,
#             elec_p, h2_p, h2o_p, hmf_p,
#             elec_ref, t, r, plant_life,
#             cur_den, cell_v, FE, fdca_y, elec_den))
