# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Creates and runs API server to power Data Commons choropleth map."""
from flask import Flask, request, jsonify
import io
import datacommons as dc
import pandas as pd
import numpy as np
import os
from routes.data import COUNTRIES

# Initialize Flask Application.
app = Flask(__name__)
app.config['SECRET_KEY'] = 'super_secret_TODO_update' # TODO

# Download country data from DataCommons.
dc.set_api_key(os.getenv("DC_SECRET_KEY"))

# TODO dynamically download certain geoJsons and cache. 
population_by_geo = {}
for geo_id, payload in dc.get_stats(COUNTRIES, "Count_Person").items():
    population_by_geo[geo_id] = next(iter(payload['data'].values()))
print("Setup Complete")

@app.route("/health")
def health():
    """ API Health Check. """
    try:
        return jsonify({"success": "true"}, 200)
    except Exception as e:
        return f"An Error Occured: {e}"

@app.route("/data")
def data():
    """Returns data for all countries for a certain statistical variable.

    API Params:
        statVar -> The statistical variable to download.
        perCapita -> Whether to return the per-capita value.

    API Returns:
        df -> dictionary of statistical variable values by country. Additionally
            includes some plotting information. 
    """
    try:
        # Get request parameters.
        statistical_variable_to_download = request.args.get("statVar")
        per_capita = request.args.get("perCapita") == "true"
        if statistical_variable_to_download == None:
            return jsonify({"error":"Must provide a statVar field!"}, 400)

        # Download statistical variable information from DataCommons.
        stat_var_by_geo = dc.get_stats(COUNTRIES,
            statistical_variable_to_download)

        # Coerce response into correct format.
        df = {}
        values = []
        for geo_id, payload in stat_var_by_geo.items():
            data = payload['data']
            first_value = next(iter(data.values()))
            # Handle per-capita option
            if per_capita:
                if geo_id in population_by_geo:
                    first_value /= population_by_geo[geo_id]
                    df[geo_id] = first_value
                    values.append(first_value)
            else:
                df[geo_id] = first_value
                values.append(first_value)

        # Add information for plot display. 
        df["_PLOTTING_INFO"] = {
            "lower_bound": np.quantile(values, 0.04),
            "upper_bound": np.quantile(values, 0.96),
        }
        # Return as json payload.
        return jsonify(df, 200)

    except Exception as e:
        return f"An Error Occured: {e}"