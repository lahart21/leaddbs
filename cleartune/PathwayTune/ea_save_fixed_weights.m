function ea_save_fixed_weights(stimfolder, opt_weights, fixed_weights_values, slider_name, pos_and_neg)

% save weights that should not be changed during optimization (fixed weights)

% opt_weights - adjustable weights
% fixed_weights_values - from the sliders in ClearTune
% slider_name - corresponds to the item (symptom) name
% pos_and_neg  - array across symptoms, 1 if both positive and negative tracts are used for the symptom

% create a json with fixed symptoms and weights      
for i = 1:length(fixed_weights_values) 
    if opt_weights{i}.Value == 0

        if pos_and_neg(i)
            % for now, split weight if both positive and negative (soft
            % side-effect) tracts are used
            % for now, weight the same for both sides
            jsonDict.fixed_symptom_weights.(genvarname([slider_name{i},'_rh'])) = fixed_weights_values(i)*0.5;
            jsonDict.fixed_symptom_weights.(genvarname([slider_name{i},'_lh'])) = fixed_weights_values(i)*0.5; 

            jsonDict.fixed_symptom_weights.(genvarname(['SE_',slider_name{i},'_rh'])) = fixed_weights_values(i)*0.5;
            jsonDict.fixed_symptom_weights.(genvarname(['SE_',slider_name{i},'_lh'])) = fixed_weights_values(i)*0.5; 
        else
            % for now, weight the same for both sides
            jsonDict.fixed_symptom_weights.(genvarname([slider_name{i},'_rh'])) = fixed_weights_values(i);
            jsonDict.fixed_symptom_weights.(genvarname([slider_name{i},'_lh'])) = fixed_weights_values(i);    
        end
    end
end

% if no fixed symptoms, create an empty dictionary
if ~exist('jsonDict','var')
    jsonDict.fixed_symptom_weights = [];
    jsonText = jsonencode(jsonDict);
    jsonText(end-2:end-1) = '{}';
else
    jsonText = jsonencode(jsonDict);
end

json_file = [stimfolder,filesep,'Fixed_symptoms.json'];
fid = fopen(json_file, 'w');
fprintf(fid, '%s', jsonText)
fclose(fid);

end