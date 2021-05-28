#!/usr/bin/python
#
#  Copyright 2017 Otto Seiskari
#  Licensed under the Apache License, Version 2.0.
#  See http://www.apache.org/licenses/LICENSE-2.0 for the full text.
#
#  This file is based on
#  https://github.com/swagger-api/swagger-ui/blob/4f1772f6544699bc748299bd65f7ae2112777abc/dist/index.html
#  (Copyright 2017 SmartBear Software, Licensed under Apache 2.0)
#
# Modified for MSVx
#

"""
Usage:

#    python swagger-yaml-to-html.py < /path/to/api.yaml > doc.html

"""
import yaml, json, os

TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Swagger UI</title>
  <link href="https://fonts.googleapis.com/css?family=Open+Sans:400,700|Source+Code+Pro:300,600|Titillium+Web:400,600,700" rel="stylesheet">
  <link rel="stylesheet" type="text/css" href="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.24.2/swagger-ui.css" >
  <style>
    html
    {
      box-sizing: border-box;
      overflow: -moz-scrollbars-vertical;
      overflow-y: scroll;
    }
    *,
    *:before,
    *:after
    {
      box-sizing: inherit;
    }

    body {
      margin:0;
      background: #fafafa;
    }
  </style>
</head>
<body>

<div id="swagger-ui"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.24.2/swagger-ui-bundle.js"> </script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/3.24.2/swagger-ui-standalone-preset.js"> </script>
<script>
window.onload = function() {

  var spec = %s;

  // Build a system
  const ui = SwaggerUIBundle({
    spec: spec,
    dom_id: '#swagger-ui',
    deepLinking: true,
    presets: [
      SwaggerUIBundle.presets.apis
    ],
    plugins: [
      SwaggerUIBundle.plugins.DownloadUrl
    ]
  })

  window.ui = ui
}
</script>
</body>

</html>
"""

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))
filename = os.path.join(__location__, "..", "docs/openapi.yaml")
try:
    with open(filename) as f:
        content = yaml.safe_load(f)
except Exception as e:
    print("Failed to read file %s" % filename)
    print(e)
spec = yaml.loads(filename, Loader=yaml.FullLoader)
new_content = TEMPLATE % json.dumps(spec)
out_filename = os.path.join(__location__, "..", "athena_app_cmdb/athena_app_cmdb/")
sys.stdout.write(TEMPLATE % json.dumps(spec))