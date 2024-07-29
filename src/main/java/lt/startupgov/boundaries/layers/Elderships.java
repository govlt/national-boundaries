package lt.startupgov.boundaries.layers;

import com.onthegomap.planetiler.FeatureCollector;
import com.onthegomap.planetiler.reader.SourceFeature;
import lt.startupgov.boundaries.constants.Layers;
import lt.startupgov.boundaries.constants.Source;

public class Elderships implements Layer {

    @Override
    public void processFeature(SourceFeature sf, FeatureCollector features) {
        if (sf.getSource().equals(Source.BOUNDARIES) && sf.getSourceLayer().equals(Layers.ELDERSHIPS) && sf.canBePolygon()) {
            var fid = sf.getLong("feature_id");

            features.polygon(Layers.ELDERSHIPS)
                    .setBufferPixels(4)
                    .setMinPixelSizeAtAllZooms(0)
                    .setId(fid)
                    .setAttr("id", fid)
                    .setAttr("name", sf.getTag("name"))
                    .setAttr("code", sf.getTag("code"))
                    .setAttr("municipality_code", sf.getTag("municipality_code"));
        }
    }
}
