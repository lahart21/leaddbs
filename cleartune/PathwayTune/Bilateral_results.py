
import numpy as np
import json
import os
import sys
import copy

def estimate_bilateral_weights(estim_w_rh_json, estim_w_lh_json, target_profiles, fixed_symptom_weights_json):

    """ Find bilateral symptoms and estimate bilateral weights accounting for possible asymmetry in fiber values

    Parameters
    ----------
    estim_w_rh_json: str, path to dict with estimated weights for right hemisphere stim
    estim_w_lh_json: str, path to dict with estimated weights for left hemisphere stim
    target_profiles: dict, Activation Profile Dictionary
    fixed_symptom_weights_json: str, path to dict with fixed weights in network blending

    """

    # "flatten" target profiles for symptoms and threshold profiles for soft side-effects
    target_profiles_and_SE = copy.deepcopy(target_profiles['profile_dict'])
    if 'Soft_SE_dict' in target_profiles_and_SE:
        target_profiles_and_SE.update(target_profiles_and_SE['Soft_SE_dict'])

    sum_symptom_vals = np.zeros(len(target_profiles_and_SE), float)

    bilateral_symptoms = {}  # store their names and sum vals across hemispheres

    for key in target_profiles_and_SE:

        if "_rh" in key:
            # internal loop to check for _lh counterpart
            for key2 in target_profiles_and_SE:
                if key2[:-3] == key[:-3] and key2 != key:

                    activ_target_profile = list(target_profiles_and_SE[key].keys())
                    sum_val_symptom_rh = 0.0
                    for i in range(len(activ_target_profile)):
                        # sum across all pathways of this symptom (separated for two sides)
                        sum_val_symptom_rh = sum_val_symptom_rh + \
                                                     target_profiles_and_SE[key][activ_target_profile[i]][2]

                    activ_target_profile = list(target_profiles_and_SE[key2].keys())
                    sum_val_symptom_lh = 0.0
                    for i in range(len(activ_target_profile)):
                        # sum across all pathways of this symptom (separated for two sides)
                        sum_val_symptom_lh = sum_val_symptom_lh + \
                                                     target_profiles_and_SE[key2][activ_target_profile[i]][2]

                    bilateral_symptoms[key[:-3]] = [sum_val_symptom_rh, sum_val_symptom_lh]

    with open(estim_w_rh_json, 'r') as fp:
        estim_w_rh = json.load(fp)
    fp.close()

    with open(estim_w_lh_json, 'r') as fp:
        estim_w_lh = json.load(fp)
    fp.close()

    with open(fixed_symptom_weights_json, 'r') as fp:
        fixed_symptom_weights = json.load(fp)
    fp.close()

    final_weights = {}

    total_weight_count = 0.0

    for key in estim_w_rh:

        # no need to re-adjust if fixed weight
        if key in fixed_symptom_weights:
            final_weights[key[:-3]] = fixed_symptom_weights[key]
        elif key[:-3] in bilateral_symptoms:

            val_coef_rh = bilateral_symptoms[key[:-3]][0] / (bilateral_symptoms[key[:-3]][0] + bilateral_symptoms[key[:-3]][1])
            val_coef_lh = bilateral_symptoms[key[:-3]][1] / (bilateral_symptoms[key[:-3]][0] + bilateral_symptoms[key[:-3]][1])

            # this is the final estimation when we have distances on both sides
            final_weights[key[:-3]] = val_coef_rh * estim_w_rh[key] + val_coef_lh * estim_w_lh[key[:-3] + '_lh']
        else:
            final_weights[key[:-3]] = estim_w_rh[key]

        total_weight_count = total_weight_count + final_weights[key[:-3]]

    # check symptoms only defined for the left hemisphere
    for key in estim_w_lh:
        if not(key[:-3] in final_weights):
            if key in fixed_symptom_weights:
                # might overwrite a value, but it is fine since fixed weights are the same for left and right
                final_weights[key[:-3]] = fixed_symptom_weights[key]
            elif not(key[:-3] in bilateral_symptoms):
                final_weights[key[:-3]] = estim_w_lh[key]

                total_weight_count = total_weight_count + final_weights[key[:-3]]

    ## we need to normalize them
    #for key in final_weights:
    #    final_weights[key] = final_weights[key] / total_weight_count

    with open(os.environ['STIMDIR'] + '/Estim_weights_bilateral_norm.json', 'w') as save_as_dict:
        json.dump(final_weights, save_as_dict)



def estimate_bilateral_improvement(estim_imp_rh_json, estim_imp_lh_json, target_profiles):

    """ Find bilateral symptoms and estimate bilateral improvement accounting for possible asymmetry in fiber values

    Parameters
    ----------
    estim_imp_rh_json: str, path to dict with predicted improvements for right hemisphere stim
    estim_imp_lh_json: str, path to dict with predicted improvements for left hemisphere stim
    target_profiles: dict, Activation Profile Dictionary

    """

    # "flatten" target profiles for symptoms and threshold profiles for soft side-effects
    target_profiles_and_SE = copy.deepcopy(target_profiles['profile_dict'])
    if 'Soft_SE_dict' in target_profiles_and_SE:
        target_profiles_and_SE.update(target_profiles_and_SE['Soft_SE_dict'])

    sum_symptom_vals = np.zeros(len(target_profiles_and_SE), float)

    bilateral_symptoms = {}  # store their names and sum vals across hemispheres

    for key in target_profiles_and_SE:

        if "_rh" in key:
            # internal loop to check for _lh counterpart
            for key2 in target_profiles_and_SE:
                if key2[:-3] == key[:-3] and key2 != key:

                    activ_target_profile = list(target_profiles_and_SE[key].keys())
                    sum_val_symptom_rh = 0.0
                    for i in range(len(activ_target_profile)):
                        # sum across all pathways of this symptom (separated for two sides)
                        sum_val_symptom_rh = sum_val_symptom_rh + \
                                                     target_profiles_and_SE[key][activ_target_profile[i]][2]

                    activ_target_profile = list(target_profiles_and_SE[key2].keys())
                    sum_val_symptom_lh = 0.0
                    for i in range(len(activ_target_profile)):
                        # sum across all pathways of this symptom (separated for two sides)
                        sum_val_symptom_lh = sum_val_symptom_lh + \
                                                     target_profiles_and_SE[key2][activ_target_profile[i]][2]

                    bilateral_symptoms[key[:-3]] = [sum_val_symptom_rh, sum_val_symptom_lh]

    with open(estim_imp_rh_json, 'r') as fp:
        estim_imp_rh = json.load(fp)
    fp.close()

    with open(estim_imp_lh_json, 'r') as fp:
        estim_imp_lh = json.load(fp)
    fp.close()

    final_imp = {}

    for key in estim_imp_rh:
        if key[:-3] in bilateral_symptoms:

            val_coef_rh = bilateral_symptoms[key[:-3]][0] / (bilateral_symptoms[key[:-3]][0] + bilateral_symptoms[key[:-3]][1])
            val_coef_lh = bilateral_symptoms[key[:-3]][1] / (bilateral_symptoms[key[:-3]][0] + bilateral_symptoms[key[:-3]][1])

            # this is the final estimation when we have distances on both sides
            final_imp[key[:-3]] = val_coef_rh * estim_imp_rh[key] + val_coef_lh * estim_imp_lh[key[:-3] + '_lh']
        else:
            final_imp[key[:-3]] = estim_imp_rh[key]

        # cap at 100%
        if final_imp[key[:-3]] > 1.0:
            final_imp[key[:-3]] = 1.0
            print("capped")


    # check symptoms only defined for the left hemisphere
    for key in estim_imp_lh:
        if not (key[:-3] in final_imp):
            final_imp[key[:-3]] = estim_imp_lh[key]

            # cap at 100%
            if final_imp[key[:-3]] > 1.0:
                final_imp[key[:-3]] = 1.0
                print("capped")

    with open(os.environ['STIMDIR'] + '/Estim_improvement_bilateral_capped.json', 'w') as save_as_dict:
        json.dump(final_imp, save_as_dict)



if __name__ == '__main__':

    # called from MATLAB
    # sys.argv[1] - stim folder
    # sys.argv[2] - reconcile_mode ('weights' or 'improvement')

    os.environ['STIMDIR'] = sys.argv[1]
    reconcile_mode = sys.argv[2]  # 'weights' or 'improvement'

    # load previously approved symptom-specific profiles
    # side is not relevant here, should be the same for bilateral
    with open(os.environ['STIMDIR'] + '/NB_rh' + '/target_profiles.json', 'r') as fp:
        target_profiles = json.load(fp)
    fixed_symptom_weights_json = os.environ['STIMDIR'] + '/Fixed_symptoms.json'

    if reconcile_mode == 'improvement':
        # estimated improvements were stored in json
        estim_imp_rh_json = os.environ['STIMDIR'] + '/NB_rh' + '/Estim_symp_improv_rh.json'
        estim_imp_lh_json = os.environ['STIMDIR'] + '/NB_lh' + '/Estim_symp_improv_lh.json'
        fp.close()
        estimate_bilateral_improvement(estim_imp_rh_json, estim_imp_lh_json, target_profiles)
    elif reconcile_mode == 'weights':
        # estimated weights were stored in json
        estim_w_rh_json = os.environ['STIMDIR'] + '/NB_rh' + '/Estim_weights_rh.json'
        estim_w_lh_json = os.environ['STIMDIR'] + '/NB_lh' + '/Estim_weights_lh.json'
        estimate_bilateral_weights(estim_w_rh_json, estim_w_lh_json, target_profiles, fixed_symptom_weights_json)

