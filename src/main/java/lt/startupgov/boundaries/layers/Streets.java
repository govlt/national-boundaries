package lt.startupgov.boundaries.layers;

import com.onthegomap.planetiler.FeatureCollector;
import com.onthegomap.planetiler.reader.SourceFeature;
import lt.startupgov.boundaries.constants.Source;

public class Streets implements Layer {

    @Override
    public void processFeature(SourceFeature sf, FeatureCollector features) {
        if (sf.getSource().equals(Source.STREETS)) {
            var fid = sf.getLong("FID");

            features.line(Source.STREETS)
                    .setBufferPixels(4)
                    .setMinPixelSizeAtAllZooms(0)
                    .setMinZoom(10)
                    .setId(fid)
                    .setAttrWithMinzoom("id", fid, 12)
                    .setAttrWithMinzoom("name", sf.getTag("GAT_PAV"), 12)
                    .setAttrWithMinzoom("full_name", sf.getTag("GAT_PAV_PI"), 12)
                    .setAttrWithMinzoom("code", sf.getTag("GAT_KODAS"), 12)
                    .setAttrWithMinzoom("length_m", sf.getTag("GAT_ILGIS"), 12)
                    .setAttrWithMinzoom("residential_area_code", sf.getTag("GYV_KODAS"), 12);
        }
    }

}
