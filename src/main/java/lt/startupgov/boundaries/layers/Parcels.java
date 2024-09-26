package lt.startupgov.boundaries.layers;

import com.onthegomap.planetiler.FeatureCollector;
import com.onthegomap.planetiler.FeatureMerge;
import com.onthegomap.planetiler.ForwardingProfile;
import com.onthegomap.planetiler.VectorTile;
import com.onthegomap.planetiler.geo.GeometryException;
import com.onthegomap.planetiler.reader.SourceFeature;
import lt.startupgov.boundaries.constants.Layers;
import lt.startupgov.boundaries.constants.Source;

import java.util.List;

public class Parcels implements Layer, ForwardingProfile.LayerPostProcesser {
    @Override
    public String name() {
        return Layers.PARCELS;
    }

    @Override
    public void processFeature(SourceFeature sf, FeatureCollector features) {
        if (sf.getSource().equals(Source.BOUNDARIES) && sf.getSourceLayer().equals(Layers.PARCELS) && sf.canBePolygon()) {
            // We do not have feature ID right now

            features.polygon(Layers.PARCELS)
                    .setBufferPixels(4)
                    .setMinPixelSizeAtAllZooms(0)
                    .setMinZoom(12)
                    .setAttr("unique_number", sf.getTag("unique_number"))
                    .setAttr("cadastral_number", sf.getTag("cadastral_number"))
                    .setAttr("status_id", sf.getTag("status_id"))
                    .setAttr("purpose_id", sf.getTag("purpose_id"))
                    .setAttr("area_ha", sf.getTag("area_ha"))
                    .setAttr("municipality_code", sf.getTag("municipality_code"))
                    .setAttr("eldership_code", sf.getTag("eldership_code"))
                    .setAttr("updated_at", sf.getTag("updated_at"))
                    .setPixelToleranceBelowZoom(13, 0.25);
        }
    }

    @Override
    public List<VectorTile.Feature> postProcess(int zoom, List<VectorTile.Feature> items) throws GeometryException {
        if (zoom >= 14) {
            return FeatureMerge.mergeMultiPolygon(items);
        }

        return FeatureMerge.mergeNearbyPolygons(items, 2, 2, 0.5, 0.5);
    }
}
