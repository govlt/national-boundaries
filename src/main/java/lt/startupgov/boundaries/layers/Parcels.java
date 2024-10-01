package lt.startupgov.boundaries.layers;

import com.onthegomap.planetiler.FeatureCollector;
import com.onthegomap.planetiler.reader.SourceFeature;
import lt.startupgov.boundaries.constants.Layers;
import lt.startupgov.boundaries.constants.Source;

public class Parcels implements Layer {

    @Override
    public void processFeature(SourceFeature sf, FeatureCollector features) {
        if (sf.getSource().equals(Source.BOUNDARIES) && sf.getSourceLayer().equals(Layers.PARCELS) && sf.canBePolygon()) {
            // We do not have feature ID right now
            var purpose_id = sf.getLong("purpose_id");
            var status_id = sf.getLong("status_id");
            var eldership_code = sf.getLong("eldership_code");
            var municipality_code = sf.getLong("municipality_code");

            features.polygon(Layers.PARCELS)
                    .setBufferPixels(4)
                    .setMinPixelSizeAtAllZooms(0)
                    .setMinZoom(14)
                    .setAttr("unique_number", sf.getLong("unique_number"))
                    .setAttr("cadastral_number", sf.getString("cadastral_number"))
                    .setAttr("status_id", status_id != 0 ? status_id : null)
                    .setAttr("purpose_id", purpose_id != 0 ? purpose_id : null)
                    .setAttr("area_ha", sf.getLong("area_ha"))
                    .setAttr("municipality_code", municipality_code != 0 ? municipality_code : null)
                    .setAttr("eldership_code", eldership_code != 0 ? eldership_code : null);
        }
    }
}
