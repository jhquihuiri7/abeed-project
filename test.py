#Validate if all features that the feature_filters depend on are in the data_feature_input list
# Validate if all features that Custom features depend on are in the data_feature_input list
# - If Either of these validations do not pass, show an error message with each feature_filter that will not be able to be created and each custom feature, along with the data feature missing
# - ex. DONE: Cannot have "{dependent custom feature name}" custom feature without "{required data feature name}" data feature (Hint: delete "{dependent custom feature name}" or reselect "{required data feature name}" data feature)
# - ex. DONE: Cannot have "{Data feature name feature filter is dependent on}" filter without "{Data feature name feature filter is dependent on}" data feature (Hint: delete "{Data feature name feature filter is dependent on}" filter or reselect "{Data feature name feature filter is dependent on}" data feature)



# Validation TODO:
# - DONE: Confirm that there is not a feature filter that is dependent on the custom feature being requested to delete
# - DONE: If There is tell the user and give a hint to delete the filter first
# - DONE: error message: Cannot delete {custome feature name} because it has a "Feature Filter" (Hint: delete {custom feature name} filter first)