package lt.startupgov.boundaries.layers;

import com.onthegomap.planetiler.FeatureCollector;
import com.onthegomap.planetiler.reader.SourceFeature;
import lt.startupgov.boundaries.constants.Source;

public class Municipalities implements Layer {

    @Override
    public void processFeature(SourceFeature sf, FeatureCollector features) {
        if (sf.getSource().equals(Source.MUNICIPALITIES) && sf.canBePolygon()) {
            var fid = sf.getLong("FID");

            features.polygon(Source.MUNICIPALITIES)
                    .setBufferPixels(4)
                    .setMinPixelSizeAtAllZooms(0)
                    .setId(fid)
                    .setAttr("id", fid)
                    .setAttr("area", sf.getTag("SAV_PLOTAS"))
                    .setAttr("code", sf.getTag("SAV_KODAS"))
                    .setAttr("county_code", sf.getTag("APS_KODAS"))
                    .setAttr("name", sf.getTag("SAV_PAV"));
        }
    }
}
