from TEA_HMFOR import HMFOR_TEA, HMFOR_inputs, HMFOR_plots
from flask import Flask, jsonify, render_template
import os
import sys
import pygal

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


@app.route('/pygal/')
def pygal_example():
    chart = pygal.Pie()
    chart.title = 'Browser usage in February 2012 (in %)'
    chart.add('IE', 19.5)
    chart.add('Firefox', 36.6)
    chart.add('Chrome', 36.3)
    chart.add('Safari', 4.5)
    chart.add('Opera', 2.3)

    chart_data1 = chart.render_data_uri()

    line_chart = pygal.Line()
    line_chart.title = 'Browser usage evolution (in %)'
    line_chart.x_labels = map(str, range(2002, 2013))
    line_chart.add('Firefox', [None, None,    0, 16.6,
                               25,   31, 36.4, 45.5, 46.3, 42.8, 37.1])
    line_chart.add('Chrome',  [None, None, None, None,
                               None, None,    0,  3.9, 10.8, 23.8, 35.3])
    line_chart.add('IE',      [85.8, 84.6, 84.7, 74.5,
                               66, 58.6, 54.7, 44.8, 36.2, 26.6, 20.1])
    line_chart.add('Others',  [14.2, 15.4, 15.3,  8.9,
                               9, 10.4,  8.9,  5.8,  6.7,  6.8,  7.5])

    chart_data2 = line_chart.render_data_uri()

    return render_template('charts.html', chart_data1=chart_data1, chart_data2=chart_data2)


@app.route('/hmfor_plots')
def hmfor_plots():

    [op_cost, op_cost_no_hmf, cap_cost] = HMFOR_plots(
        HMFOR_inputs, 0.02, 0.06, 1, 2, 0.8, 1, 0.8, 1)
    return render_template('charts.html', op_cost=op_cost, op_cost_no_hmf=op_cost_no_hmf, cap_cost=cap_cost)


if __name__ == '__main__':
    app.run(debug=True)

# print(HMFOR_TEA(prod, prod_price, op_time,
#             elec_p, h2_p, h2o_p, hmf_p,
#             elec_ref, t, r, plant_life,
#             cur_den, cell_v, FE, fdca_y, elec_den))
