package lt.startupgov.boundaries.layers;

import com.onthegomap.planetiler.FeatureCollector;
import com.onthegomap.planetiler.reader.SourceFeature;
import lt.startupgov.boundaries.constants.Source;

public class Elderships implements Layer {

    @Override
    public void processFeature(SourceFeature sf, FeatureCollector features) {
        if (sf.getSource().equals(Source.ELDERSHIPS) && sf.canBePolygon()) {
            var fid = sf.getLong("FID");

            features.polygon(Source.ELDERSHIPS)
                    .setBufferPixels(4)
                    .setMinPixelSizeAtAllZooms(0)
                    .setId(fid)
                    .setAttr("id", fid)
                    .setAttr("name", sf.getTag("SEN_PAV"))
                    .setAttr("code", sf.getTag("SEN_KODAS"))
                    .setAttr("area", sf.getTag("SEN_PLOTAS"))
                    .setAttr("municipality_code", sf.getTag("SAV_KODAS"));
        }
    }
}
