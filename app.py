from TEA_HMFOR import HMFOR_TEA, HMFOR_inputs, HMFOR_plots
from flask import Flask, jsonify, render_template, request
import sys

app = Flask(__name__)


@app.route('/')
def hello_world():
    return ""


@app.route('/form')
def form():
    return render_template('form.html')


@app.route('/form_response', methods=["POST"])
def form_response():
    try:
        # Add in validation to ensure that numbers cannot be out of range (% > 1)

        # Fetching values from the form
        prod = validateNum(request.form.get("prod"), 100000.0)
        prod_price = validateNum(request.form.get("prod_price"), 1445.0)
        op_time = validateNum(request.form.get("op_time"), 350.0)
        elec_p = validateNum(request.form.get("elec_p"), 0.02)
        h2_p = validateNum(request.form.get("h2_p"), 1.5)
        h2o_p = validateNum(request.form.get("h2o_p"), 0.00143)
        hmf_p = validateNum(request.form.get("hmf_p"), 0.9095)
        elec_ref = validateNum(request.form.get("elec_ref"), 920.0)
        t = validateNum(request.form.get("t"), 0.389)
        r = validateNum(request.form.get("r"), 0.1)
        plant_life = validateNum(request.form.get("plant_life"), 20.0)
        cur_den = validateNum(request.form.get("cur_den"), 0.05)
        cell_v = validateNum(request.form.get("cell_v"), 1.4)
        FE = validateNum(request.form.get("FE"), 1.0)
        fdca_y = validateNum(request.form.get("fdca_y"), 0.98)
        elec_den = validateNum(request.form.get("elec_den"), 2.13)
        cd_low = validateNum(request.form.get("cd_low"), 0.02)
        cd_high = validateNum(request.form.get("cd_high"), 0.06)
        cv_low = validateNum(request.form.get("cv_low"), 1.0)
        cv_high = validateNum(request.form.get("cv_high"), 2.0)
        fe_low = validateNum(request.form.get("fe_low"), 0.8)
        fe_high = validateNum(request.form.get("fe_high"), 1.0)
        yld_low = validateNum(request.form.get("yld_low"), 0.8)
        yld_high = validateNum(request.form.get("yld_high"), 1.0)

        HMFOR_inputs = [prod, prod_price, op_time,
                        elec_p, h2_p, h2o_p, hmf_p,
                        elec_ref, t, r, plant_life,
                        cur_den, cell_v, FE, fdca_y, elec_den]
        [NPV, payback_time, product_income, op_costs,
            cap_costs] = HMFOR_TEA(*HMFOR_inputs)

        [op_cost, op_cost_no_hmf, cap_cost, SA_output,
            cd_cv_output, fe_cv_output, yld_cv_output, cd_npv_output] = HMFOR_plots(
                HMFOR_inputs, cd_low, cd_high, cv_low, cv_high, fe_low, fe_high, yld_low, yld_high)

        # Extracting values of StringIO
        SA = SA_output.getvalue()
        cd_cv = cd_cv_output.getvalue()
        fe_cv = fe_cv_output.getvalue()
        yld_cv = yld_cv_output.getvalue()
        cd_npv = cd_npv_output.getvalue()

        return render_template('form.html', prod=prod, prod_price=prod_price, op_time=op_time,
                               elec_p=elec_p, h2_p=h2_p, h2o_p=h2o_p, hmf_p=hmf_p,
                               elec_ref=elec_ref, t=t, r=r, plant_life=plant_life,
                               cur_den=cur_den, cell_v=cell_v, FE=FE, fdca_y=fdca_y, elec_den=elec_den, NPV=NPV, payback_time=payback_time,
                               cd_low=cd_low, cd_high=cd_high, cv_low=cv_low, cv_high=cv_high,
                               fe_low=fe_low, fe_high=fe_high, yld_low=yld_low, yld_high=yld_high, op_cost=op_cost, op_cost_no_hmf=op_cost_no_hmf, cap_cost=cap_cost, SA=SA, cd_cv=cd_cv, fe_cv=fe_cv, yld_cv=yld_cv, cd_npv=cd_npv)
    except Exception as e:
        return "The following error has occured: " + str(e)

# Sample endpoint: /HMFOR/production=100000.0/fdca_p=1445.0/t_op=350.0/elec_p=0.02/h2_p=1.5/h2o_p=0.00143/hmf_p=0.9095/elec_ref=920.0/t=0.389/r=0.1/plant_life=20.0/cur_den=0.05/cell_v=1.4/FE=1.0/fdca_y=0.98/elec_den=2.13


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

# Sample endpoint: /hmfor_plots/production=100000.0/fdca_p=1445.0/t_op=350.0/elec_p=0.02/h2_p=1.5/h2o_p=0.00143/hmf_p=0.9095/elec_ref=920.0/t=0.389/r=0.1/plant_life=20.0/cur_den=0.05/cell_v=1.4/FE=1.0/fdca_y=0.98/elec_den=2.13/cd_low=0.02/cd_high=0.06/cv_low=1.0/cv_high=2.0/fe_low=0.8/fe_high=1.0/yld_low=0.8/yld_high=1.0/


@app.route('/hmfor_plots/production=<float:prod>/fdca_p=<float:prod_price>/t_op=<float:op_time>/elec_p=<float:elec_p>/h2_p=<float:h2_p>/h2o_p=<float:h2o_p>/hmf_p=<float:hmf_p>/elec_ref=<float:elec_ref>/t=<float:t>/r=<float:r>/plant_life=<float:plant_life>/cur_den=<float:cur_den>/cell_v=<float:cell_v>/FE=<float:FE>/fdca_y=<float:fdca_y>/elec_den=<float:elec_den>/cd_low=<float:cd_low>/cd_high=<float:cd_high>/cv_low=<float:cv_low>/cv_high=<float:cv_high>/fe_low=<float:fe_low>/fe_high=<float:fe_high>/yld_low=<float:yld_low>/yld_high=<float:yld_high>/', methods=['GET'])
def hmfor_plots(prod, prod_price, op_time,
                elec_p, h2_p, h2o_p, hmf_p,
                elec_ref, t, r, plant_life,
                cur_den, cell_v, FE, fdca_y, elec_den,
                cd_low, cd_high, cv_low, cv_high,
                fe_low, fe_high, yld_low, yld_high):
    try:
        HMFOR_inputs = [prod, prod_price, op_time,
                        elec_p, h2_p, h2o_p, hmf_p,
                        elec_ref, t, r, plant_life,
                        cur_den, cell_v, FE, fdca_y, elec_den]

        [op_cost, op_cost_no_hmf, cap_cost, SA_output,
         cd_cv_output, fe_cv_output, yld_cv_output, cd_npv_output] = HMFOR_plots(
            HMFOR_inputs, cd_low, cd_high, cv_low, cv_high, fe_low, fe_high, yld_low, yld_high)

        # Extracting values of StringIO
        SA = SA_output.getvalue()
        cd_cv = cd_cv_output.getvalue()
        fe_cv = fe_cv_output.getvalue()
        yld_cv = yld_cv_output.getvalue()
        cd_npv = cd_npv_output.getvalue()

        return render_template('charts.html', op_cost=op_cost, op_cost_no_hmf=op_cost_no_hmf, cap_cost=cap_cost, SA=SA, cd_cv=cd_cv, fe_cv=fe_cv, yld_cv=yld_cv, cd_npv=cd_npv)
    except Exception as e:
        return "The following error has occured: " + str(e)


def validateNum(variable, default):
    if (not variable) or float(variable) <= 0.0:
        return default
    else:
        return float(variable)


if __name__ == '__main__':
    app.run(debug=True)

# print(HMFOR_TEA(prod, prod_price, op_time,
#             elec_p, h2_p, h2o_p, hmf_p,
#             elec_ref, t, r, plant_life,
#             cur_den, cell_v, FE, fdca_y, elec_den))
