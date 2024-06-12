'use strict';

import _ from 'lodash';
import filtersMixin from 'moleculer-knex-filters';

const DbService = require('@moleculer/database').Service;

export default function (opts: any = {}) {
  const adapter: any = {
    type: 'Knex',
    options: {
      knex: opts.config,
      tableName: opts.collection,
    },
  };

  opts = _.defaultsDeep(opts, { adapter }, { cache: false });

  const schema = {
    mixins: [DbService(opts), filtersMixin()],

    actions: {
      findOne(ctx: any) {
        return this.findEntity(ctx);
      },

      removeAllEntities(ctx: any) {
        return this.clearEntities(ctx);
      },
    },

    merged(schema: any) {
      if (schema.actions) {
        for (const action in schema.actions) {
          const params = schema.actions[action].additionalParams;
          if (typeof params === 'object') {
            schema.actions[action].params = {
              ...schema.actions[action].params,
              ...params,
            };
          }
        }
      }
    },
  };

  return schema;
}
