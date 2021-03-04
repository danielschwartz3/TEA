from TEA_HMFOR import HMFOR_TEA
from flask import Flask, jsonify
import os

app = Flask(__name__)


@app.route('/')
def hello_world():
    return jsonify({"about": 'Hello, World!'})


@app.route('/HMFOR/production=<float:prod>/fdca_p=<float:prod_price>/t_op=<float:op_time>/elec_p=<float:elec_p>/h2_p=<float:h2_p>/h2o_p=<float:h2o_p>/hmf_p=<float:hmf_p>/elec_ref=<float:elec_ref>/t=<float:t>/r=<float:r>/plant_life=<float:plant_life>/cur_den=<float:cur_den>/cell_v=<float:cell_v>/FE=<float:FE>/fdca_y=<float:fdca_y>/elec_den=<float:elec_den>', methods=['GET'])
def hmfor(prod, prod_price, op_time,
          elec_p, h2_p, h2o_p, hmf_p,
          elec_ref, t, r, plant_life,
          cur_den, cell_v, FE, fdca_y, elec_den):
    [NPV, payback_time] = HMFOR_TEA(prod, prod_price, op_time,
                                    elec_p, h2_p, h2o_p, hmf_p,
                                    elec_ref, t, r, plant_life,
                                    cur_den, cell_v, FE, fdca_y, elec_den)
    return jsonify({"NPV": NPV, "payback_time": payback_time})


if __name__ == '__main__':
    app.run(debug=True)

# print(HMFOR_TEA(prod, prod_price, op_time,
#             elec_p, h2_p, h2o_p, hmf_p,
#             elec_ref, t, r, plant_life,
#             cur_den, cell_v, FE, fdca_y, elec_den))
