const { test, describe } = require('node:test');
const assert = require('node:assert');

class MockEntity {
    constructor(data) {
        this.index = data.index;
        this.x = data.x;
        this.y = data.y;
        this.x_new = data.x;
        this.y_new = data.y;
        this.hp = data.hp;
        this.hp_new = data.hp;
        this.deleted = false;
    }

    update_data(data) {
        this.x = this.x_new;
        this.y = this.y_new;
        this.x_new = data.x;
        this.y_new = data.y;
        this.hp = this.hp_new;
        this.hp_new = data.hp;
    }

    delete() {
        this.deleted = true;
    }
}

class MockMapSync {
    constructor() {
        this.objects = {};
        this.tiles = {};
        this.particles = {};
        this.player_id = "0";
        this.player_obj = null;
        this.epoch = 0;
    }

    sync(mapData) {
        if (this.epoch === mapData.global_params.epoch) {
            return false;
        }
        this.epoch = mapData.global_params.epoch;

        // Sync objects: add or update
        Object.entries(mapData.objects).forEach(([i, objData]) => {
            if (!this.objects.hasOwnProperty(i)) {
                this.objects[i] = new MockEntity(objData);
            } else {
                this.objects[i].update_data(objData);
            }
        });

        // Delete missing objects
        Object.entries(this.objects).forEach(([i, obj]) => {
            if (!mapData.objects.hasOwnProperty(i)) {
                obj.delete();
                delete this.objects[i];
            }
        });

        // Resolve player object
        this.player_id = mapData.player.object_id;
        if (mapData.player.object_type === 'object') {
            this.player_obj = this.objects[this.player_id];
        } else if (mapData.player.object_type === 'tile') {
            this.player_obj = this.tiles[this.player_id];
        }

        return true;
    }
}

describe('Frontend Map State Sync', () => {
    test('initial state sync adds entities', () => {
        const map = new MockMapSync();
        const payload = {
            global_params: { epoch: 1, status: 'running' },
            player: { object_id: '1', object_type: 'object' },
            objects: {
                '1': { index: 1, x: 2, y: 2, hp: 100 },
                '2': { index: 2, x: 4, y: 5, hp: 50 },
            },
            tiles: {},
            particles: {},
        };

        const refreshed = map.sync(payload);
        assert.strictEqual(refreshed, true);
        assert.strictEqual(Object.keys(map.objects).length, 2);
        assert.strictEqual(map.player_obj.index, 1);
        assert.strictEqual(map.player_obj.hp, 100);
    });

    test('sequential state sync updates existing and removes missing', () => {
        const map = new MockMapSync();
        map.sync({
            global_params: { epoch: 1 },
            player: { object_id: '1', object_type: 'object' },
            objects: {
                '1': { index: 1, x: 2, y: 2, hp: 100 },
                '2': { index: 2, x: 4, y: 5, hp: 50 },
            },
        });

        // Epoch 2: object '2' dies (removed), object '1' moves to (3, 2), object '3' spawns
        const payloadEpoch2 = {
            global_params: { epoch: 2 },
            player: { object_id: '1', object_type: 'object' },
            objects: {
                '1': { index: 1, x: 3, y: 2, hp: 99 },
                '3': { index: 3, x: 8, y: 8, hp: 20 },
            },
        };

        map.sync(payloadEpoch2);

        assert.strictEqual(Object.keys(map.objects).length, 2);
        assert.strictEqual(map.objects.hasOwnProperty('2'), false);
        assert.strictEqual(map.objects['1'].x_new, 3);
        assert.strictEqual(map.objects['1'].hp_new, 99);
        assert.strictEqual(map.objects['3'].x_new, 8);
    });

    test('ignores duplicate epoch sync calls', () => {
        const map = new MockMapSync();
        const payload = {
            global_params: { epoch: 1 },
            player: { object_id: '1', object_type: 'object' },
            objects: { '1': { index: 1, x: 2, y: 2, hp: 100 } },
        };

        assert.strictEqual(map.sync(payload), true);
        assert.strictEqual(map.sync(payload), false);
    });
});
