#!/bin/bash
python z_web/manage.py dump_object presupuestos.itempresupuesto --query '{"revision__presupuesto__centro_costo__pk": 95}' > /tmp/presupuesto.json
python z_web/manage.py dump_object costos.costo --query '{"centro_costo__pk": 95}' > /tmp/costos.json
python z_web/manage.py dump_object costos.avanceobra --query '{"centro_costo__pk": 95}' > /tmp/avanceobra.json
python z_web/manage.py dump_object registro.certificacionitem --query '{"certificacion__obra__pk": 95}' > /tmp/certificacion.json
python z_web/manage.py merge_fixtures /tmp/presupuesto.json /tmp/costos.json /tmp/certificacion.json /tmp/avanceobra.json > fixtures/demo-os.json

rm /tmp/presupuesto.json /tmp/costos.json /tmp/avanceobra.json /tmp/certificacion.json
