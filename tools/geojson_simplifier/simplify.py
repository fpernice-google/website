# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Simplifies GeoJson files by reducing their number of vertices.

    Some geographic boundaries are more complicated than the finest detail
    shown in browsers. Simplifying the boundaries makes them an order of
    magnitude smaller so they load faster without much, if any, loss of detail.

    Typical usage:
    python3 simplify.py --in_path original-data/geoId-01.geojson
                        --out_path simplified-data/geoId-01-simple.geojson
                        --verbose
"""

import rdp
import geojson
from absl import app
from absl import flags


FLAGS = flags.FLAGS
flags.DEFINE_string('in_path', default=None,
                    help='Path to original GeoJSON to simplify.')
flags.DEFINE_string('out_path', default=None,
                    help='Path to save simplified GeoJSON.')
flags.DEFINE_boolean('verbose', default=False,
                     help='If True, compression information is printed.')
flags.DEFINE_float('epsilon', default=0.01,
                   help='Epsilon parameter to the Ramer–Douglas–Peucker '
                        'algorithm. For more information, see the Wikipedia'
                        ' page.')
flags.register_validator('epsilon', lambda value: value > 0,
                         message='--epsilon must be positive')
flags.mark_flag_as_required('in_path')
flags.mark_flag_as_required('out_path')


class GeojsonSimplifier:
    """Simplifies GeoJson files by reducing their number of vertices.

    Attributes:
        geojson: Initially, the GeoJSON containing the Polygon or MultiPolygon
                 to be simplified. After calling simplify(), it contains the
                 simplified GeoJSON.
    """
    def __init__(self):
        self.geojson = None

    def read_geojson(self, in_path):
        """Reads GeoJSON from input file and stores it in instance geojson.

        Args:
            in_path: A string representing the path to the original GeoJSON to
                     be processed.
        """
        with open(in_path, 'r') as f:
            self.geojson = geojson.load(f)
            if not self.geojson.is_valid:
                raise ValueError("Invalid GeoJSON read in.")

    def simplify(self, epsilon=0.01, verbose=False):
        """Modifies the instance geojson by reducing its number of points.

        Runs the Ramer–Douglas–Peucker algorithm to simplify the GeoJSONs.

        Args:
            epsilon: The epsilon parameter to the  Ramer–Douglas–Peucker
                     algorithm. See the Wikipedia page for details.
            verbose: If True, the number of points in the GeoJSON before and
                     after simplification will be printed for comparison.
        """
        coords = self.geojson['coordinates']

        original_sz = 0
        simplified_sz = 0
        # Iterate over polygons.
        for i in range(len(coords)):
            assert len(coords[i]) == 1
            c = coords[i][0]
            original_sz += len(c)
            new_c = rdp.rdp(c, epsilon=epsilon)
            simplified_sz += len(new_c)
            if len(new_c) >= 3:
                # Simplify the polygon succeeded, not yielding a line
                coords[i][0] = new_c

        if verbose:
            print(f"Original number of points = {original_sz}.")
        if verbose:
            print(f"Simplified number of points = {simplified_sz}.")

    def save(self, out_path):
        """Saves instance geojson after simplification.

        Args:
            out_path: A string representing the path to the GeoJSON in which to
                      save the result.
        """
        with open(out_path, 'w') as f:
            geojson.dump(self.geojson, f)


def main(_):
    simplifier = GeojsonSimplifier()
    simplifier.read_geojson(FLAGS.in_path)
    simplifier.simplify(FLAGS.epsilon, FLAGS.verbose)
    simplifier.save(FLAGS.out_path)


if __name__ == '__main__':
    app.run(main)