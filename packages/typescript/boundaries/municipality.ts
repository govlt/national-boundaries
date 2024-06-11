import {HttpReader} from "flatgeobuf/lib/mjs/http-reader";
import {Geometry, IFeature, Rect} from "flatgeobuf";
import {fromFeature} from "flatgeobuf/lib/mjs/ol/feature";
import {bbox} from '@turf/turf'
import {AllGeoJSON} from "@turf/helpers";
import {fromGeometry} from "flatgeobuf/lib/mjs/geojson/geometry";

export class MunicipaliesReader {
    private reader: HttpReader;

    private constructor(
        reader: HttpReader,
    ) {
        this.reader = reader;
    }

    static async open(url: string = "https://cdn.biip.lt/tiles/poc/boundaries/municipalities.fgb", nocache: boolean = false,): Promise<MunicipaliesReader> {
        const reader = await HttpReader.open(url, false);

        return new MunicipaliesReader(reader);
    }

    async* list(boundingGeoJson: AllGeoJSON): AsyncGenerator<IFeature, void, unknown> {
        const boundingBox = bbox(boundingGeoJson);
        const boundingBoxRect: Rect = {
            minX: boundingBox[0],
            minY: boundingBox[1],
            maxX: boundingBox[2],
            maxY: boundingBox[3]
        };

        for await (const _feature of this.reader.selectBbox(boundingBoxRect)) {
            const geometry = fromGeometry(
                _feature.geometry() as Geometry,
                this.reader.header.geometryType,
            );

            yield fromFeature(_feature, this.reader.header);
        }
    }

    count(): number {
        return this.reader.header.featuresCount;
    }
}
