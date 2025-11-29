import joblib
# You must import the class definition so pickle knows what 'Multiregressor' is
from xgb_model import Multiregressor 
import pandas as pd
from datetime import datetime
from hyperparameter_optimizer import create_features
import pandas as pd
from datetime import datetime

# 1. Definir fechas
start_date = "2025-09-01"
end_date = datetime.today()
# Load the object
loaded_model = joblib.load("data/regressor.joblib")

# You can now use it directly

predictions = loaded_model.predict(X_test)