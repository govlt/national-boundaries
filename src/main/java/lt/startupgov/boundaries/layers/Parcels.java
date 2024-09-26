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

            features.polygon(Layers.PARCELS)
                    .setBufferPixels(4)
                    .setMinPixelSizeAtAllZooms(0)
                    .setMinZoom(10)
                    .setAttr("unique_number", sf.getTag("unique_number"))
                    .setAttr("cadastral_number", sf.getTag("cadastral_number"))
                    .setAttr("status_id", sf.getTag("status_id"))
                    .setAttr("purpose_id", sf.getTag("purpose_id"))
                    .setAttr("area_ha", sf.getTag("area_ha"))
                    .setAttr("municipality_code", sf.getTag("municipality_code"))
                    .setAttr("eldership_code", sf.getTag("eldership_code"))
                    .setAttr("updated_at", sf.getTag("updated_at"));
        }
    }

}
