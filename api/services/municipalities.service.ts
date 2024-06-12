'use strict';

import moleculer, {Context} from 'moleculer';
import {Service} from 'moleculer-decorators';

import DbConnection from '../mixins/database.mixin';

import {boundariesConfig} from '../knexfile';
import {CREATE_ONLY_READ_ACTIONS} from '../types';

@Service({
    name: 'municipalities',

    mixins: [
        DbConnection({
            collection: 'municipalities',
            config: boundariesConfig,
            createActions: CREATE_ONLY_READ_ACTIONS,
        })
    ],

    settings: {
        fields: {
            code: {
                type: 'string',
                columnType: 'integer',
                columnName: 'code',
                primaryKey: true,
                secure: true,
            },

            geom: {
                type: 'any',
                hidden: "byDefault",
                geom: {
                    type: 'geom',
                },
            },

            name: 'string',
            area: 'number',
            county: {
                type: 'string',
                columnName: 'countyCode',
                populate: (ctx: Context, values: string[]) =>
                    ctx.call('counties.resolve', {code: values, mapping: true}),
            },
        },
    },
})
export default class MunicipalitiesService extends moleculer.Service {
}
