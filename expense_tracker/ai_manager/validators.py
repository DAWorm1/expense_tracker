from django.core.validators import RegexValidator

class CSV_Validator(RegexValidator):
    regex = ",(?=(?:[^\"]*\"[^\"]*\")*(?![^\"]*\"))"
