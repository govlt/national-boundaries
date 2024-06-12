'use strict';

import moleculer from 'moleculer';
import {Service} from 'moleculer-decorators';

import DbConnection from '../mixins/database.mixin';

import {boundariesConfig} from '../knexfile';
import {CREATE_ONLY_READ_ACTIONS} from '../types';

@Service({
    name: 'counties',

    mixins: [
        DbConnection({
            collection: 'counties',
            config: boundariesConfig,
            createActions: CREATE_ONLY_READ_ACTIONS,
        }),
    ],

    settings: {
        fields: {
            code: {
                type: 'string',
                columnType: 'integer',
                primaryKey: true,
                secure: true,
            },

            geom: {
                type: 'any',
                geom: {
                    type: 'geom',
                },
            },

            name: 'string',
            area: 'number',
        },
    },
})
export default class CountiesService extends moleculer.Service {
}
