package lt.startupgov.boundaries.layers;

import com.onthegomap.planetiler.FeatureCollector;
import com.onthegomap.planetiler.reader.SourceFeature;
import lt.startupgov.boundaries.constants.Layers;
import lt.startupgov.boundaries.constants.Source;

public class Municipalities implements Layer {

    @Override
    public void processFeature(SourceFeature sf, FeatureCollector features) {
        if (sf.getSource().equals(Source.BOUNDARIES) && sf.getSourceLayer().equals(Layers.MUNICIPALITIES) && sf.canBePolygon()) {
            var fid = sf.getLong("feature_id");

            features.polygon(Layers.MUNICIPALITIES)
                    .setBufferPixels(4)
                    .setMinPixelSizeAtAllZooms(0)
                    .setId(fid)
                    .setAttr("id", fid)
                    .setAttr("code", sf.getTag("code"))
                    .setAttr("county_code", sf.getTag("county_code"))
                    .setAttr("name", sf.getTag("name"));
        }
    }
}
