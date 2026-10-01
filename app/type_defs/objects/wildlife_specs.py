"""Pure-data description of the extended ecosystem.

Kept free of game imports so it can be read by the type registry, the
ecosystem regulator and the sprite generator without circular imports.

Stage kinds:
    egg      - stationary, hatches into the next stage after ``hatch_time``
    juvenile - moves and eats, grows into the next stage after ``grow_time``
    pupa     - stationary, turns into the next stage after ``pupa_time``
    adult    - moves, eats and lays the first stage every ``lay_time``
"""

# ---------------------------------------------------------------------------
# Animals (new species). Every animal has at least three development stages.
# ---------------------------------------------------------------------------
ANIMALS = {
    "Rabbit": {
        "breed_hp": 45,
        "breed_cost": 10,
        "rgb": (230, 230, 230),
        "lay_time": 60,
        "hatch_time": 60,
        "grow_time": 80,
        "hp_skip": 4,
        "speed": 1.0,
        "stages": [
            {
                "name": "RabbitNest",
                "kind": "egg",
                "image": "rabbit_nest",
                "prompt": (
                    "a small round nest of dry grass and white fur with three tiny"
                    " sleeping pink newborn rabbits"
                ),
                "desc": (
                    "A fur-lined nest of newborn rabbits. The kits leave the nest after"
                    " a while."
                ),
            },
            {
                "name": "Bunny",
                "kind": "juvenile",
                "image": "bunny",
                "prompt": (
                    "tiny cute baby car decorated as a fluffy grey baby bunny, short"
                    " round ears on the roof, pink nose on the front bumper, cotton"
                    " tail at the rear"
                ),
                "desc": (
                    "A young rabbit. Eats clover, carrots and dandelions and grows into"
                    " a rabbit."
                ),
            },
            {
                "name": "Rabbit",
                "kind": "adult",
                "image": "rabbit",
                "prompt": (
                    "sports car decorated as a white rabbit, white fur texture on the"
                    " body, two long rabbit ears folded back along the roof, black eyes"
                    " and pink nose on the front bumper, fluffy round tail on the rear"
                    " bumper"
                ),
                "desc": (
                    "A fast herbivore. Eats clover, carrots and dandelions. Hunted by"
                    " foxes, wolves and owls."
                ),
            },
        ],
        "diet": {
            "CloverSeed": 5,
            "Fern": 10,
            "WheatStalks": 15,
            "Apple": 10,
            "Sunflower": 10,
            "Pumpkin": 10,
            "BerryBush": 10,
            "Grass": 15,
            "Grass3": 15,
            "StrawberryPatch": 15,
            "MossCarpet": 5,
            "Strawberry": 15,
            "StrawberryRunner": 10,
            "WheatSprout": 15,
            "Clover": 20,
            "Carrot": 30,
            "Dandelion": 20,
            "Grass2": 15,
            "CarrotSeed": 5,
        },
    },
    "Deer": {
        "rgb": (153, 102, 51),
        "lay_time": 120,
        "hatch_time": 80,
        "grow_time": 120,
        "hp_skip": 5,
        "speed": 1.0,
        "stages": [
            {
                "name": "DeerNewborn",
                "kind": "egg",
                "image": "deer_newborn",
                "prompt": (
                    "a newborn spotted fawn curled up asleep in a bed of flattened"
                    " grass"
                ),
                "desc": "A newborn fawn hiding motionless in the grass.",
            },
            {
                "name": "Fawn",
                "kind": "juvenile",
                "image": "fawn",
                "prompt": (
                    "small cute car decorated as a baby fawn, light brown paint with"
                    " white spots on the roof, big dark eyes and black nose on the"
                    " front bumper, tiny white tail at the rear"
                ),
                "desc": "A young deer. Browses ferns and berry bushes.",
            },
            {
                "name": "Deer",
                "kind": "adult",
                "image": "deer",
                "prompt": (
                    "elegant car decorated as a red deer stag, brown fur paint, large"
                    " branching antlers mounted on the hood, dark eyes and black nose"
                    " on the front bumper, white tail at the rear"
                ),
                "desc": (
                    "A large herbivore browsing ferns, berry bushes and oak saplings."
                    " Prey of wolves and bears."
                ),
            },
        ],
        "diet": {
            "Strawberry": 10,
            "StrawberryPatch": 15,
            "Clover": 15,
            "Dandelion": 15,
            "Sunflower": 15,
            "WheatStalks": 15,
            "Hazelnut": 10,
            "HazelBush": 15,
            "BlackberryBramble": 15,
            "Blackberry": 10,
            "Pumpkin": 15,
            "Carrot": 15,
            "Grass": 15,
            "Grass2": 15,
            "Apple": 20,
            "AppleSapling": 15,
            "PineSeedling": 15,
            "SaltDeposit": 15,
            "MossCarpet": 10,
            "Fern": 25,
            "BerryBush": 25,
            "OakTree": 20,
            "Grass3": 15,
            "Acorn": 10,
        },
    },
    "Mouse": {
        "breed_hp": 45,
        "breed_cost": 10,
        "rgb": (128, 128, 128),
        "lay_time": 50,
        "hatch_time": 50,
        "grow_time": 60,
        "hp_skip": 5,
        "speed": 1.0,
        "stages": [
            {
                "name": "MouseNest",
                "kind": "egg",
                "image": "mouse_nest",
                "prompt": (
                    "a tiny ball-shaped nest of shredded straw and leaves with pink"
                    " newborn mice inside"
                ),
                "desc": "A straw nest full of newborn mice.",
            },
            {
                "name": "MousePup",
                "kind": "juvenile",
                "image": "mouse_pup",
                "prompt": (
                    "tiny cute toy car decorated as a baby grey mouse, round ears on"
                    " the roof, pink nose and whiskers on the front, thin pink tail at"
                    " the rear"
                ),
                "desc": "A young mouse foraging for seeds.",
            },
            {
                "name": "Mouse",
                "kind": "adult",
                "image": "mouse",
                "prompt": (
                    "small compact car decorated as a grey field mouse, big round ears"
                    " on the roof, whiskers and pink nose on the front bumper, long"
                    " thin pink tail trailing from the rear"
                ),
                "desc": "A seed eater. Food for foxes, snakes and owls.",
            },
        ],
        "diet": {
            "Apple": 5,
            "Blackberry": 5,
            "PineCone": 5,
            "LotusSeed": 5,
            "MossSpore": 5,
            "FernSpore": 5,
            "Caterpillar": 5,
            "WheatGrain": 10,
            "Hazelnut": 10,
            "Strawberry": 10,
            "LithopsSeed": 5,
            "SunflowerSeed": 10,
            "Acorn": 10,
            "BerrySeed": 10,
            "PumpkinSeed": 10,
            "Seed": 10,
            "CarrotSeed": 10,
            "ReedSeed": 10,
            "Seed2": 10,
            "Seed3": 10,
            "DandelionSeed": 10,
            "CloverSeed": 10,
            "CactusSeed": 10,
        },
    },
    "Squirrel": {
        "breed_hp": 45,
        "breed_cost": 10,
        "rgb": (204, 85, 0),
        "lay_time": 90,
        "hatch_time": 60,
        "grow_time": 90,
        "hp_skip": 5,
        "speed": 1.0,
        "stages": [
            {
                "name": "SquirrelDrey",
                "kind": "egg",
                "image": "squirrel_drey",
                "prompt": (
                    "a round squirrel nest made of twigs and dry leaves with baby"
                    " squirrels peeking out"
                ),
                "desc": "A twig nest (drey) with squirrel kits.",
            },
            {
                "name": "SquirrelKit",
                "kind": "juvenile",
                "image": "squirrel_kit",
                "prompt": (
                    "tiny cute car decorated as a baby red squirrel, orange fur paint,"
                    " small tufted ears on the roof, big fluffy curled tail at the rear"
                ),
                "desc": "A young squirrel collecting acorns.",
            },
            {
                "name": "Squirrel",
                "kind": "adult",
                "image": "squirrel",
                "prompt": (
                    "sporty car decorated as a red squirrel, orange fur paint, tufted"
                    " ears on the roof, black eyes and nose on the front bumper, huge"
                    " fluffy bushy tail curling over the rear"
                ),
                "desc": (
                    "Eats acorns and seeds and raids owl nests. Hunted by foxes and"
                    " owls."
                ),
            },
        ],
        "diet": {
            "Strawberry": 10,
            "Blackberry": 10,
            "Sunflower": 10,
            "WheatGrain": 10,
            "CactusSeed": 5,
            "Caterpillar": 10,
            "ButterflyEgg": 10,
            "Seed": 5,
            "Seed2": 5,
            "PineCone": 15,
            "Hazelnut": 15,
            "Apple": 10,
            "Acorn": 15,
            "SunflowerSeed": 10,
            "Mushroom2": 15,
            "BerrySeed": 10,
            "PumpkinSeed": 10,
            "OwlEgg": 20,
            "Mushroom": 15,
            "Seed3": 10,
            "FernSpore": 10,
        },
    },
    "Snail": {
        "breed_hp": 45,
        "breed_cost": 10,
        "rgb": (179, 136, 255),
        "lay_time": 70,
        "hatch_time": 60,
        "grow_time": 90,
        "hp_skip": 6,
        "speed": 0.4,
        "stages": [
            {
                "name": "SnailEgg",
                "kind": "egg",
                "image": "snail_egg",
                "prompt": (
                    "a small cluster of shiny translucent pearly white snail eggs on a"
                    " leaf"
                ),
                "desc": "A clutch of snail eggs.",
            },
            {
                "name": "BabySnail",
                "kind": "juvenile",
                "image": "baby_snail",
                "prompt": (
                    "tiny cute car decorated as a baby snail, small spiral shell on the"
                    " roof, two short eye stalks on the front"
                ),
                "desc": "A young snail slowly munching leaves.",
            },
            {
                "name": "Snail",
                "kind": "adult",
                "image": "snail",
                "prompt": (
                    "compact beetle car with four visible black wheels, glossy grey"
                    " paint, a big brown spiral snail shell mounted on the roof, two"
                    " eye stalks sticking up from the front bumper, headlights"
                ),
                "desc": (
                    "A slow herbivore that eats ferns, pumpkins and mushrooms. Food for"
                    " frogs, hedgehogs and badgers."
                ),
            },
        ],
        "diet": {
            "Strawberry": 10,
            "Dandelion": 10,
            "Sunflower": 10,
            "Reed": 10,
            "Apple": 10,
            "Mushroom2": 10,
            "MossSpore": 5,
            "Grass": 10,
            "WheatSprout": 10,
            "StrawberryRunner": 10,
            "StrawberryPatch": 15,
            "LotusBud": 10,
            "MossTuft": 10,
            "MossCarpet": 15,
            "Fern": 15,
            "Pumpkin": 20,
            "Mushroom": 15,
            "Clover": 10,
            "Carrot": 10,
        },
    },
    "Butterfly": {
        "breed_hp": 45,
        "breed_cost": 10,
        "rgb": (255, 102, 204),
        "lay_time": 60,
        "hatch_time": 50,
        "grow_time": 70,
        "pupa_time": 50,
        "hp_skip": 5,
        "speed": 1.0,
        "stages": [
            {
                "name": "ButterflyEgg",
                "kind": "egg",
                "image": "butterfly_egg",
                "prompt": (
                    "a tiny cluster of pale green ribbed butterfly eggs on a leaf"
                ),
                "desc": "Butterfly eggs laid on a leaf.",
            },
            {
                "name": "Caterpillar",
                "kind": "juvenile",
                "image": "caterpillar",
                "prompt": (
                    "long segmented car decorated as a green caterpillar, round green"
                    " body segments with yellow spots, small antennae on the front"
                ),
                "desc": "A hungry larva eating leaves. Turns into a chrysalis.",
                "speed": 0.5,
                "diet": {
                    "StrawberryPatch": 10,
                    "BerryBush": 10,
                    "OakTree": 10,
                    "BrambleSprout": 10,
                    "Strawberry": 5,
                    "AppleSapling": 10,
                    "HazelSapling": 10,
                    "Clover": 15,
                    "Sunflower": 15,
                    "Dandelion": 15,
                    "Fern": 10,
                },
            },
            {
                "name": "Chrysalis",
                "kind": "pupa",
                "image": "chrysalis",
                "prompt": (
                    "a jade green butterfly chrysalis with tiny golden dots lying on a"
                    " leaf"
                ),
                "desc": "A chrysalis. A butterfly is forming inside.",
            },
            {
                "name": "Butterfly",
                "kind": "adult",
                "image": "butterfly",
                "prompt": (
                    "small car decorated as a monarch butterfly, large orange and black"
                    " patterned wings spread out on both sides, thin antennae on the"
                    " front"
                ),
                "desc": "Drinks nectar from flowers. Eaten by frogs and owls.",
            },
        ],
        "diet": {
            "StrawberryPatch": 10,
            "Apple": 10,
            "Cactus": 10,
            "LivingStones": 5,
            "Pumpkin": 10,
            "LotusBud": 5,
            "Sunflower": 10,
            "Dandelion": 10,
            "Clover": 10,
            "BerryBush": 10,
            "LotusFlower": 10,
            "BlackberryBramble": 10,
        },
    },
    "Tortoise": {
        "breed_hp": 45,
        "breed_cost": 10,
        "rgb": (85, 107, 47),
        "lay_time": 110,
        "hatch_time": 90,
        "grow_time": 120,
        "hp_skip": 7,
        "speed": 0.4,
        "stages": [
            {
                "name": "TortoiseEgg",
                "kind": "egg",
                "image": "tortoise_egg",
                "prompt": (
                    "three round white leathery tortoise eggs in a shallow sandy hollow"
                ),
                "desc": "Tortoise eggs buried in the sand.",
            },
            {
                "name": "TortoiseHatchling",
                "kind": "juvenile",
                "image": "tortoise_hatchling",
                "prompt": (
                    "tiny cute car decorated as a baby tortoise, small domed patterned"
                    " shell on the roof, little head at the front"
                ),
                "desc": "A young tortoise.",
            },
            {
                "name": "Tortoise",
                "kind": "adult",
                "image": "tortoise",
                "prompt": (
                    "sturdy car decorated as a giant tortoise, high domed hexagon"
                    " patterned brown and olive shell on the roof, wrinkly head at the"
                    " front and stubby legs at the corners"
                ),
                "desc": (
                    "A slow, long-lived herbivore that eats cacti, pumpkins and reeds."
                ),
            },
        ],
        "diet": {
            "Clover": 15,
            "Grass": 10,
            "Apple": 15,
            "Blackberry": 10,
            "WheatSprout": 10,
            "Carrot": 15,
            "Fern": 10,
            "MossCarpet": 10,
            "Grass2": 10,
            "Strawberry": 15,
            "StrawberryPatch": 15,
            "LivingStones": 20,
            "LithopsSprout": 10,
            "LotusFlower": 15,
            "Cactus": 30,
            "Pumpkin": 25,
            "Dandelion": 15,
            "Reed": 15,
            "BerryBush": 15,
            "CactusSeed": 10,
        },
    },
    "Frog": {
        "breed_hp": 45,
        "breed_cost": 10,
        "rgb": (0, 153, 51),
        "lay_time": 70,
        "hatch_time": 50,
        "grow_time": 70,
        "hp_skip": 6,
        "speed": 1.0,
        "stages": [
            {
                "name": "Frogspawn",
                "kind": "egg",
                "image": "frogspawn",
                "prompt": (
                    "a clump of clear jelly frogspawn with black dots in a small puddle"
                    " of water"
                ),
                "desc": "A clump of frog eggs.",
            },
            {
                "name": "Tadpole",
                "kind": "juvenile",
                "image": "tadpole",
                "prompt": (
                    "small car decorated as a dark tadpole, round black glossy body and"
                    " a long wavy tail at the rear"
                ),
                "desc": "A tadpole eating reeds. Grows into a frog.",
                "diet": {
                    "MossTuft": 5,
                    "LotusBud": 10,
                    "LotusSeed": 10,
                    "MossSpore": 5,
                    "Reed": 10,
                    "ReedSeed": 10,
                },
            },
            {
                "name": "Frog",
                "kind": "adult",
                "image": "frog",
                "prompt": (
                    "compact car decorated as a green tree frog, bright green glossy"
                    " paint, big bulging eyes on the front corners of the roof, webbed"
                    " feet at the four corners"
                ),
                "desc": "Eats insects and snails. Prey of snakes, owls and bears.",
            },
        ],
        "diet": {
            "SnailEgg": 10,
            "MousePup": 15,
            "Spore": 5,
            "Tadpole": 10,
            "Butterfly": 30,
            "Caterpillar": 25,
            "Chrysalis": 15,
            "Snail": 20,
            "BabySnail": 15,
            "Bee": 30,
            "ButterflyEgg": 10,
            "Spore2": 5,
        },
    },
    "Hedgehog": {
        "breed_hp": 45,
        "breed_cost": 10,
        "rgb": (102, 51, 0),
        "lay_time": 90,
        "hatch_time": 60,
        "grow_time": 90,
        "hp_skip": 6,
        "speed": 0.8,
        "stages": [
            {
                "name": "HedgehogNest",
                "kind": "egg",
                "image": "hedgehog_nest",
                "prompt": (
                    "a nest of dry autumn leaves with tiny pale baby hedgehogs with"
                    " soft white spines"
                ),
                "desc": "A leaf nest of baby hedgehogs.",
            },
            {
                "name": "Hoglet",
                "kind": "juvenile",
                "image": "hoglet",
                "prompt": (
                    "tiny cute car decorated as a baby hedgehog, short soft pale spines"
                    " covering the roof, little pointed snout with black nose on the"
                    " front"
                ),
                "desc": "A young hedgehog.",
            },
            {
                "name": "Hedgehog",
                "kind": "adult",
                "image": "hedgehog",
                "prompt": (
                    "round car decorated as a hedgehog, the whole roof covered in brown"
                    " spikes, pointed snout with a shiny black nose on the front bumper"
                ),
                "desc": "Eats snails, caterpillars and snake eggs.",
            },
        ],
        "diet": {
            "Frogspawn": 10,
            "Tadpole": 10,
            "MouseNest": 15,
            "MousePup": 15,
            "Apple": 10,
            "ChickenEgg": 15,
            "TortoiseEgg": 15,
            "Blackberry": 10,
            "Strawberry": 10,
            "Snail": 25,
            "BabySnail": 15,
            "SnailEgg": 10,
            "Caterpillar": 20,
            "Chrysalis": 15,
            "ButterflyEgg": 10,
            "SnakeEgg": 20,
            "Mushroom": 10,
            "Mushroom2": 10,
            "BerrySeed": 10,
            "Spore": 5,
        },
    },
    "Snake": {
        "rgb": (153, 204, 0),
        "lay_time": 110,
        "hatch_time": 80,
        "grow_time": 100,
        "hp_skip": 6,
        "speed": 1.0,
        "stages": [
            {
                "name": "SnakeEgg",
                "kind": "egg",
                "image": "snake_egg",
                "prompt": "a clutch of five oval leathery cream colored snake eggs",
                "desc": "A clutch of snake eggs.",
            },
            {
                "name": "SnakeHatchling",
                "kind": "juvenile",
                "image": "snake_hatchling",
                "prompt": (
                    "small slim car decorated as a baby green snake, long thin body"
                    " stretched behind, small head with a forked red tongue at the"
                    " front"
                ),
                "desc": "A young snake.",
            },
            {
                "name": "Snake",
                "kind": "adult",
                "image": "snake",
                "prompt": (
                    "long slim car decorated as a python snake, yellow and green scale"
                    " pattern, long tail stretching behind, snake head with forked red"
                    " tongue on the front bumper"
                ),
                "desc": "Hunts mice, frogs and raids nests. Hunted by owls and bears.",
            },
        ],
        "diet": {
            "Squirrel": 30,
            "Hoglet": 20,
            "Rabbit": 30,
            "Chicken": 30,
            "RabbitNest": 20,
            "HedgehogNest": 15,
            "SquirrelDrey": 15,
            "Mouse": 40,
            "MousePup": 25,
            "MouseNest": 20,
            "Frog": 40,
            "Tadpole": 15,
            "Frogspawn": 10,
            "ChickenEgg": 25,
            "Chick": 25,
            "OwlEgg": 25,
            "Owlet": 20,
            "Bunny": 30,
            "SquirrelKit": 25,
            "TortoiseEgg": 20,
        },
    },
    "Owl": {
        "rgb": (140, 115, 85),
        "lay_time": 110,
        "hatch_time": 80,
        "grow_time": 100,
        "hp_skip": 7,
        "speed": 1.0,
        "stages": [
            {
                "name": "OwlEgg",
                "kind": "egg",
                "image": "owl_egg",
                "prompt": "two round white owl eggs in a nest of twigs and feathers",
                "desc": "Owl eggs in a twig nest.",
            },
            {
                "name": "Owlet",
                "kind": "juvenile",
                "image": "owlet",
                "prompt": (
                    "tiny cute car decorated as a fluffy baby owl, white downy"
                    " feathers, huge round yellow eyes on the front"
                ),
                "desc": "A fluffy young owl.",
            },
            {
                "name": "Owl",
                "kind": "adult",
                "image": "owl",
                "prompt": (
                    "car decorated as a brown barn owl, feather pattern paint, wide"
                    " feathered wings folded along the sides, round face with big eyes"
                    " and a hooked beak on the front"
                ),
                "desc": "A night hunter of mice, frogs, snakes and squirrels.",
            },
        ],
        "diet": {
            "Tadpole": 10,
            "Caterpillar": 10,
            "Snail": 15,
            "BabySnail": 10,
            "FoxKit": 20,
            "BadgerCub": 20,
            "SnakeEgg": 15,
            "Mouse": 40,
            "MousePup": 25,
            "Frog": 35,
            "SnakeHatchling": 25,
            "Snake": 40,
            "Squirrel": 40,
            "SquirrelKit": 25,
            "Bunny": 30,
            "Butterfly": 15,
            "Chick": 25,
            "Hoglet": 20,
            "Chicken": 40,
            "Rabbit": 40,
        },
    },
    "Wolf": {
        "rgb": (77, 77, 102),
        "lay_time": 140,
        "hatch_time": 80,
        "grow_time": 120,
        "hp_skip": 5,
        "speed": 1.0,
        "stages": [
            {
                "name": "WolfDen",
                "kind": "egg",
                "image": "wolf_den",
                "prompt": (
                    "a small earthen den entrance among rocks with two grey wolf pups"
                    " sleeping inside"
                ),
                "desc": "A den with newborn wolf pups.",
            },
            {
                "name": "WolfPup",
                "kind": "juvenile",
                "image": "wolf_pup",
                "prompt": (
                    "small cute car decorated as a grey wolf pup, fluffy grey fur"
                    " paint, pointy ears on the roof, black nose on the front"
                ),
                "desc": "A playful young wolf.",
            },
            {
                "name": "Wolf",
                "kind": "adult",
                "image": "wolf",
                "prompt": (
                    "muscular sports car decorated as a grey wolf, grey and white fur"
                    " paint, pointed ears on the roof, fierce yellow eyes and black"
                    " nose on the front bumper, bushy tail at the rear"
                ),
                "desc": "An apex predator hunting deer, cows, foxes and rabbits.",
            },
        ],
        "diet": {
            "Chicken": 30,
            "Chick": 20,
            "Mouse": 15,
            "Squirrel": 25,
            "Snake": 25,
            "Frog": 15,
            "BearCub": 25,
            "TortoiseHatchling": 15,
            "RabbitNest": 20,
            "ChickenEgg": 15,
            "Deer": 50,
            "Fawn": 40,
            "DeerNewborn": 30,
            "Cow": 50,
            "Calf": 40,
            "Fox": 50,
            "FoxKit": 30,
            "Rabbit": 40,
            "Bunny": 25,
            "Tortoise": 30,
            "Hedgehog": 20,
            "Hoglet": 15,
            "Badger": 40,
            "BadgerCub": 30,
        },
    },
    "Bear": {
        "rgb": (92, 51, 23),
        "lay_time": 200,
        "hatch_time": 90,
        "grow_time": 140,
        "hp_skip": 4,
        "speed": 0.8,
        "stages": [
            {
                "name": "BearDen",
                "kind": "egg",
                "image": "bear_den",
                "prompt": (
                    "a cozy cave den lined with moss with two tiny sleeping brown bear"
                    " cubs"
                ),
                "desc": "A den with newborn bear cubs.",
            },
            {
                "name": "BearCub",
                "kind": "juvenile",
                "image": "bear_cub",
                "prompt": (
                    "small chubby cute car decorated as a brown bear cub, fluffy brown"
                    " fur paint, round ears on the roof, black nose on the front"
                ),
                "desc": "A young bear.",
            },
            {
                "name": "Bear",
                "kind": "adult",
                "image": "bear",
                "prompt": (
                    "big bulky truck decorated as a brown grizzly bear, thick brown fur"
                    " paint, round ears on the roof, big snout with black nose on the"
                    " front bumper, huge paws with claws at the corners"
                ),
                "desc": (
                    "An omnivore eating berries, acorns, honeycombs, deer, wolves and"
                    " tortoises."
                ),
            },
        ],
        "diet": {
            "Strawberry": 15,
            "StrawberryPatch": 20,
            "HazelBush": 15,
            "PineCone": 10,
            "Mushroom": 15,
            "Cow": 40,
            "Calf": 30,
            "Rabbit": 30,
            "Fox": 30,
            "Badger": 30,
            "Chicken": 25,
            "Snail": 10,
            "Hedgehog": 20,
            "Squirrel": 20,
            "WheatStalks": 15,
            "LotusFlower": 10,
            "Sunflower": 15,
            "Apple": 25,
            "Blackberry": 20,
            "BlackberryBramble": 20,
            "Hazelnut": 15,
            "BerryBush": 30,
            "Acorn": 15,
            "Pumpkin": 25,
            "BeeEgg": 40,
            "Deer": 50,
            "Fawn": 40,
            "Tortoise": 30,
            "Wolf": 50,
            "WolfPup": 30,
            "WolfDen": 20,
            "Snake": 30,
            "Frog": 20,
            "Carrot": 15,
            "Mushroom2": 15,
        },
    },
}

# Diets of the original animals (the new species carry their diets above).
EXISTING_ANIMAL_DIETS = {
    "Cow": {
        "Apple": 15,
        "AppleSapling": 10,
        "AppleTree": 20,
        "BerrySeed": 15,
        "BerryBush": 20,
        "Blackberry": 15,
        "BrambleSprout": 10,
        "BlackberryBramble": 20,
        "CarrotSeed": 10,
        "Carrot": 20,
        "CloverSeed": 10,
        "DandelionSeed": 10,
        "FernSpore": 10,
        "Fern": 20,
        "Hazelnut": 10,
        "HazelSapling": 10,
        "HazelBush": 20,
        "LotusSeed": 10,
        "LotusBud": 10,
        "LotusFlower": 20,
        "MossSpore": 10,
        "MossTuft": 10,
        "MossCarpet": 20,
        "Acorn": 10,
        "OakTree": 20,
        "PineCone": 10,
        "PineSeedling": 10,
        "PineTree": 20,
        "PumpkinSeed": 10,
        "Pumpkin": 20,
        "ReedSeed": 10,
        "Reed": 20,
        "SaltGrain": 10,
        "SaltCrystal": 10,
        "Strawberry": 15,
        "StrawberryRunner": 10,
        "StrawberryPatch": 20,
        "SunflowerSeed": 10,
        "Sunflower": 20,
        "WheatGrain": 10,
        "WheatStalks": 20,
        "WheatSprout": 15,
        "WheatGrain": 10,
        "SaltDeposit": 15,
        "SaltGrain": 10,
        "Seed": 10,
        "Seed2": 10,
        "Seed3": 10,
        "Grass": 25,
        "Grass2": 25,
        "Grass3": 25,
        "CarnivorousFlowerSeed": 10,
        "Clover": 25,
        "CloverSeed": 10,
        "Dandelion": 25,
        "DandelionSeed": 10,
        "Strawberry": 30,
        "StrawberryPatch": 25,
        "StrawberryRunner": 15,
        "Carrot": 30,
        "CarrotSeed": 20,
        "Pumpkin": 20,
        "Sunflower": 15,
        "SunflowerSeed": 10,
        "BerryBush": 20,
        "Blackberry": 10,
        "BlackberryBramble": 15,
        "Apple": 15,
        "AppleSapling": 10,
        "OakTree": 20,
        "Acorn": 10,
        "PineTree": 15,
        "PineCone": 15,
        "PineSeedling": 10,
        "Fern": 20,
        "FernSpore": 10,
        "Reed": 20,
        "ReedSeed": 10,
        "LotusFlower": 15,
        "LotusBud": 10,
        "LotusSeed": 10,
        "MossCarpet": 15,
        "MossTuft": 10,
        "MossSpore": 5,
        "LivingStones": 10,
        "LithopsSprout": 10,
        "LithopsSeed": 5,
        "Cactus": 10,
        "CactusSeed": 5,
        "HazelBush": 15,
        "Hazelnut": 15,
        "HazelSapling": 10,
    },
    "Chicken": {
        "BerrySeed": 10,
        "PumpkinSeed": 10,
        "CarrotSeed": 10,
        "ReedSeed": 10,
        "Blackberry": 10,
        "Apple": 10,
        "BabySnail": 10,
        "SnailEgg": 10,
        "ButterflyEgg": 10,
        "FernSpore": 5,
        "MossSpore": 5,
        "Spore": 5,
        "Spore2": 5,
        "WheatGrain": 10,
        "SaltGrain": 5,
        "Strawberry": 10,
        "Seed": 10,
        "Seed2": 10,
        "Seed3": 10,
        "SunflowerSeed": 10,
        "DandelionSeed": 10,
        "CloverSeed": 10,
        "Caterpillar": 20,
    },
    "Fox": {
        "Frog": 30,
        "Hoglet": 20,
        "OwlEgg": 20,
        "TortoiseEgg": 15,
        "Strawberry": 10,
        "Apple": 10,
        "Butterfly": 10,
        "SnakeEgg": 15,
        "Blackberry": 10,
        "Cow": 50,
        "Calf": 40,
        "Chicken": 50,
        "Chick": 30,
        "Badger": 50,
        "BadgerCub": 30,
        "CowEgg": 25,
        "ChickenEgg": 25,
        "BadgerEgg": 25,
        "Rabbit": 50,
        "Bunny": 30,
        "RabbitNest": 25,
        "Mouse": 30,
        "MousePup": 20,
        "MouseNest": 15,
        "Squirrel": 40,
        "SquirrelKit": 25,
    },
    "Badger": {
        "Strawberry": 10,
        "Apple": 10,
        "MouseNest": 15,
        "MousePup": 15,
        "Frog": 20,
        "HedgehogNest": 15,
        "Caterpillar": 10,
        "Acorn": 10,
        "BerrySeed": 10,
        "WheatGrain": 5,
        "Hazelnut": 10,
        "Blackberry": 10,
        "Mushroom": 50,
        "Mushroom2": 50,
        "Spore": 5,
        "Spore2": 5,
        "Snail": 30,
        "BabySnail": 20,
        "SnailEgg": 10,
        "TortoiseEgg": 20,
        "Carrot": 15,
    },
    "Bee": {
        "Fox": 50,
        "Cow": 50,
        "Seed": 1,
        "Seed2": 1,
        "Seed3": 1,
        "Spore": 1,
        "Spore2": 1,
        "Chicken": 50,
        "Badger": 50,
        "CowEgg": 25,
        "ChickenEgg": 25,
        "Bear": 50,
    },
}

# Add the original standard animals to the same stage schema as the newer species.
ANIMALS.update(
    {
        "Cow": {
            "rgb": (0, 0, 0),
            "diet": EXISTING_ANIMAL_DIETS["Cow"],
            "lay_time": 50,
            "hatch_time": 100,
            "grow_time": 80,
            "hp_skip": 1,
            "speed": 1.0,
            "stages": [
                {
                    "name": "CowEgg",
                    "kind": "egg",
                    "image": "egg",
                    "prompt": "a white egg in a small nest",
                    "desc": "An egg that will hatch into a calf.",
                    "rgb": (255, 255, 255),
                },
                {
                    "name": "Calf",
                    "kind": "juvenile",
                    "image": "calf",
                    "prompt": (
                        "small cute car decorated as a baby calf, white paint with"
                        " black patches, tiny ears on the roof, pink nose on the front"
                    ),
                    "desc": (
                        "A young cow. Grazes on grass and seeds and grows into a cow."
                    ),
                    "rgb": (60, 60, 60),
                    "hp_skip": 1,
                },
                {
                    "name": "Cow",
                    "kind": "adult",
                    "image": "cow",
                    "prompt": "a top-down game sprite of a black and white dairy cow",
                    "desc": (
                        "Animal representing a cow that moves, eats plants, eat seeds"
                        " and lays eggs. A cow can be eaten by a fox."
                    ),
                },
            ],
        },
        "Chicken": {
            "rgb": (255, 204, 51),
            "diet": EXISTING_ANIMAL_DIETS["Chicken"],
            "lay_time": 350,
            "hatch_time": 100,
            "grow_time": 80,
            "hp_skip": 3,
            "speed": 1.0,
            "stages": [
                {
                    "name": "ChickenEgg",
                    "kind": "egg",
                    "image": "egg",
                    "prompt": "a white chicken egg resting in straw",
                    "desc": "An egg that will hatch into chicken.",
                    "rgb": (255, 255, 255),
                },
                {
                    "name": "Chick",
                    "kind": "juvenile",
                    "image": "chick",
                    "prompt": (
                        "tiny cute round car decorated as a fluffy yellow baby chick,"
                        " small orange beak on the front"
                    ),
                    "desc": "A young chicken pecking at seeds.",
                    "rgb": (255, 230, 100),
                    "hp_skip": 3,
                },
                {
                    "name": "Chicken",
                    "kind": "adult",
                    "image": "chicken",
                    "prompt": "a top-down game sprite of a brown hen with a red comb",
                    "desc": (
                        "Animal representing a chicken that can move, eats seeds and"
                        " caterpillars and lays eggs. Chicken can be eaten by a fox."
                    ),
                    "uses_code": False,
                },
            ],
        },
        "Fox": {
            "rgb": (255, 153, 0),
            "diet": EXISTING_ANIMAL_DIETS["Fox"],
            "lay_time": 202,
            "hatch_time": 100,
            "grow_time": 100,
            "hp_skip": 3,
            "speed": 1.0,
            "stages": [
                {
                    "name": "FoxEgg",
                    "kind": "egg",
                    "image": "egg",
                    "prompt": "a small fox egg nestled in dry leaves",
                    "desc": "An egg that will hatch into a fox.",
                    "rgb": (255, 255, 255),
                },
                {
                    "name": "FoxKit",
                    "kind": "juvenile",
                    "image": "fox_kit",
                    "prompt": (
                        "small cute car decorated as a baby fox kit, fluffy orange fur"
                        " paint, big pointed ears on the roof, white chest and black"
                        " nose on the front, white tipped tail at the rear"
                    ),
                    "desc": "A young fox.",
                    "rgb": (255, 180, 80),
                    "hp_skip": 3,
                },
                {
                    "name": "Fox",
                    "kind": "adult",
                    "image": "fox",
                    "prompt": (
                        "a top-down game sprite of a red fox with a white-tipped tail"
                    ),
                    "desc": (
                        "An animal representing a fox. A fox moves, eats chickens,"
                        " cows, rabbits, mice, squirrels and eggs. Foxes can also lay"
                        " eggs."
                    ),
                    "uses_code": False,
                },
            ],
        },
        "Badger": {
            "rgb": (0, 0, 0),
            "diet": EXISTING_ANIMAL_DIETS["Badger"],
            "lay_time": 50,
            "hatch_time": 100,
            "grow_time": 80,
            "hp_skip": 1,
            "speed": 1.0,
            "stages": [
                {
                    "name": "BadgerEgg",
                    "kind": "egg",
                    "image": "egg",
                    "prompt": "a white egg tucked into a grass nest",
                    "desc": "An egg that will hatch into a badger.",
                    "rgb": (255, 255, 255),
                },
                {
                    "name": "BadgerCub",
                    "kind": "juvenile",
                    "image": "badger_cub",
                    "prompt": (
                        "small cute car decorated as a baby badger, grey fur paint with"
                        " a black and white striped face on the front"
                    ),
                    "desc": "A young badger.",
                    "rgb": (40, 40, 40),
                    "hp_skip": 1,
                },
                {
                    "name": "Badger",
                    "kind": "adult",
                    "image": "badger",
                    "prompt": (
                        "a top-down game sprite of a European badger with bold black"
                        " and white facial stripes"
                    ),
                    "desc": (
                        "Animal representing a badger that moves, eats mushrooms,"
                        " snails and tortoise eggs and lays eggs. A badger can be eaten"
                        " by a fox or a wolf."
                    ),
                },
            ],
        },
    }
)

# Animals trapped by the carnivorous flower when they step into it.
CARNIVOROUS_FLOWER_PREY = {
    "Cow": 50,
    "Chicken": 50,
    "Fox": 50,
    "Rabbit": 40,
    "Mouse": 20,
    "Frog": 20,
    "Deer": 50,
    "Wolf": 50,
    "Bear": 50,
    "Owl": 40,
    "Tortoise": 40,
}

# ---------------------------------------------------------------------------
# Plants (new species): seed -> plant.
# ---------------------------------------------------------------------------
PLANTS = {
    "Grass": {
        "rgb": (0, 204, 0),
        "emit_time": 40,
        "sprout_time": 30,
        "lifespan_skip": 12,
        "seed": {
            "name": "Seed",
            "image": "seed",
            "rgb": (255, 204, 0),
            "prompt": "a small golden seed",
            "desc": "A seed that turns into a flower",
        },
        "plant": {
            "name": "Grass",
            "image": "grass",
            "prompt": "a patch of green grass",
            "desc": "Grass is a plant. Grass can produce seeds.",
        },
    },
    "Grass2": {
        "rgb": (0, 204, 0),
        "emit_time": 40,
        "sprout_time": 30,
        "lifespan_skip": 12,
        "seed": {
            "name": "Seed2",
            "image": "seed2",
            "rgb": (255, 204, 0),
            "prompt": "a small golden seed",
            "desc": "A seed that turns into a flower",
        },
        "plant": {
            "name": "Grass2",
            "image": "grass2",
            "prompt": "a patch of green grass",
            "desc": "Grass is a plant. Grass can produce seeds.",
        },
    },
    "Grass3": {
        "rgb": (0, 204, 0),
        "emit_time": 40,
        "sprout_time": 30,
        "lifespan_skip": 12,
        "seed": {
            "name": "Seed3",
            "image": "seed3",
            "rgb": (255, 204, 0),
            "prompt": "a small golden seed",
            "desc": "A seed that turns into a flower",
        },
        "plant": {
            "name": "Grass3",
            "image": "grass3",
            "prompt": "a patch of green grass",
            "desc": "Grass is a plant. Grass can produce seeds.",
        },
    },
    "Clover": {
        "rgb": (51, 153, 51),
        "emit_time": 35,
        "sprout_time": 30,
        "lifespan_skip": 12,
        "seed": {
            "name": "CloverSeed",
            "image": "clover_seed",
            "prompt": "a few tiny heart shaped yellow-brown clover seeds",
            "desc": "A clover seed.",
        },
        "plant": {
            "name": "Clover",
            "image": "clover",
            "prompt": (
                "a lush patch of green three-leaf clover with a few round white-pink"
                " clover blossoms"
            ),
            "desc": "A clover patch loved by rabbits and cows.",
        },
    },
    "Sunflower": {
        "rgb": (255, 204, 0),
        "emit_time": 60,
        "sprout_time": 35,
        "lifespan_skip": 12,
        "seed": {
            "name": "SunflowerSeed",
            "image": "sunflower_seed",
            "prompt": "a single striped black and white sunflower seed",
            "desc": "A sunflower seed. Favourite of mice, squirrels and chickens.",
        },
        "plant": {
            "name": "Sunflower",
            "image": "sunflower",
            "prompt": (
                "a big sunflower head with bright yellow petals and a brown seed center"
                " surrounded by large green leaves"
            ),
            "desc": "A sunflower producing seeds.",
        },
    },
    "BerryBush": {
        "rgb": (153, 0, 76),
        "emit_time": 40,
        "sprout_time": 40,
        "lifespan_skip": 20,
        "seed": {
            "name": "BerrySeed",
            "image": "berry_seed",
            "prompt": "a single ripe dark purple blueberry",
            "desc": "A berry carrying the seed of a berry bush.",
        },
        "plant": {
            "name": "BerryBush",
            "image": "berry_bush",
            "prompt": (
                "a round leafy green bush full of clusters of red raspberries and dark"
                " blueberries"
            ),
            "desc": "A berry bush. Deer, bears and tortoises love it.",
        },
    },
    "Cactus": {
        "rgb": (0, 102, 51),
        "emit_time": 120,
        "sprout_time": 45,
        "lifespan_skip": 25,
        "seed": {
            "name": "CactusSeed",
            "image": "cactus_seed",
            "prompt": "a small pink prickly pear cactus fruit",
            "desc": "A cactus fruit with seeds.",
        },
        "plant": {
            "name": "Cactus",
            "image": "cactus",
            "prompt": (
                "a round green barrel cactus with ribs, white spines and a pink flower"
                " on top"
            ),
            "desc": "A hardy cactus. Only tortoises dare to eat it.",
        },
    },
    "Fern": {
        "rgb": (34, 139, 34),
        "emit_time": 35,
        "sprout_time": 30,
        "lifespan_skip": 15,
        "seed": {
            "name": "FernSpore",
            "image": "fern_spore",
            "prompt": "a tiny curled up green fern fiddlehead sprout",
            "desc": "A fern spore sprouting into a fiddlehead.",
        },
        "plant": {
            "name": "Fern",
            "image": "fern",
            "prompt": (
                "a lush green fern with long feathery fronds spreading out in a circle"
            ),
            "desc": "A fern eaten by deer, snails and caterpillars.",
        },
    },
    "Reed": {
        "rgb": (153, 153, 51),
        "emit_time": 50,
        "sprout_time": 30,
        "lifespan_skip": 12,
        "seed": {
            "name": "ReedSeed",
            "image": "reed_seed",
            "prompt": (
                "a thick fluffy brown cattail seed head bursting with white fluff"
            ),
            "desc": "A fluffy reed seed.",
        },
        "plant": {
            "name": "Reed",
            "image": "reed",
            "prompt": (
                "a clump of tall green reeds and brown cattails growing from a small"
                " pool of water"
            ),
            "desc": "Reeds feeding tadpoles and tortoises.",
        },
    },
    "Pumpkin": {
        "rgb": (255, 128, 0),
        "emit_time": 40,
        "sprout_time": 40,
        "lifespan_skip": 15,
        "seed": {
            "name": "PumpkinSeed",
            "image": "pumpkin_seed",
            "prompt": "a single flat cream colored pumpkin seed",
            "desc": "A pumpkin seed.",
        },
        "plant": {
            "name": "Pumpkin",
            "image": "pumpkin",
            "prompt": (
                "a big ripe orange pumpkin on a curly green vine with broad leaves"
            ),
            "desc": "A pumpkin on the vine.",
        },
    },
    "Dandelion": {
        "rgb": (255, 255, 102),
        "emit_time": 30,
        "sprout_time": 25,
        "lifespan_skip": 10,
        "seed": {
            "name": "DandelionSeed",
            "image": "dandelion_seed",
            "prompt": "a round white fluffy dandelion seed head puffball",
            "desc": "A fluffy dandelion seed head.",
        },
        "plant": {
            "name": "Dandelion",
            "image": "dandelion",
            "prompt": (
                "a rosette of jagged green dandelion leaves with three bright yellow"
                " dandelion flowers"
            ),
            "desc": "A dandelion.",
        },
    },
    "OakTree": {
        "rgb": (0, 77, 0),
        "emit_time": 50,
        "sprout_time": 50,
        "lifespan_skip": 30,
        "seed": {
            "name": "Acorn",
            "image": "acorn",
            "prompt": "a single shiny brown acorn with its textured cap",
            "desc": "An acorn that grows into an oak.",
        },
        "plant": {
            "name": "OakTree",
            "image": "oak_tree",
            "prompt": (
                "a round leafy oak tree crown with lobed green leaves and a few acorns"
            ),
            "desc": "A young oak tree dropping acorns.",
        },
    },
    "Carrot": {
        "rgb": (255, 102, 0),
        "emit_time": 35,
        "sprout_time": 30,
        "lifespan_skip": 12,
        "seed": {
            "name": "CarrotSeed",
            "image": "carrot_seed",
            "prompt": "a few tiny ridged brown carrot seeds",
            "desc": "Carrot seeds.",
        },
        "plant": {
            "name": "Carrot",
            "image": "carrot",
            "prompt": (
                "an orange carrot top poking out of the soil with a bushy tuft of green"
                " leaves"
            ),
            "desc": "A carrot. A rabbit favourite.",
        },
    },
}

# ---------------------------------------------------------------------------
# Three-stage plants, stones and minerals: seed -> sapling -> mature.
# The mature stage drops seeds/berries/nuts/grains, which restart the cycle.
# ---------------------------------------------------------------------------
PLANTS.update(
    {
        "AppleTree": {
            "rgb": (204, 0, 0),
            "emit_time": 60,
            "sprout_time": 30,
            "grow_time": 50,
            "lifespan_skip": 25,
            "seed": {
                "name": "Apple",
                "image": "apple",
                "prompt": "a single shiny red apple with a small green leaf",
                "desc": "A fallen apple. Its seeds grow into an apple tree.",
            },
            "sapling": {
                "name": "AppleSapling",
                "image": "apple_sapling",
                "prompt": "a young apple tree sapling with a few fresh green leaves",
                "desc": "A young apple tree.",
            },
            "plant": {
                "name": "AppleTree",
                "image": "apple_tree",
                "prompt": "a round leafy apple tree crown full of bright red apples",
                "desc": "An apple tree dropping apples. Deer and bears love them.",
            },
        },
        "PineTree": {
            "rgb": (0, 90, 60),
            "emit_time": 70,
            "sprout_time": 35,
            "grow_time": 60,
            "lifespan_skip": 30,
            "seed": {
                "name": "PineCone",
                "image": "pine_cone",
                "prompt": "a single brown woody pine cone",
                "desc": "A pine cone full of seeds. Squirrels hoard them.",
            },
            "sapling": {
                "name": "PineSeedling",
                "image": "pine_seedling",
                "prompt": "a tiny pine seedling with a star of soft green needles",
                "desc": "A young pine.",
            },
            "plant": {
                "name": "PineTree",
                "image": "pine_tree",
                "prompt": (
                    "a tall evergreen pine tree seen from above, layered dark green"
                    " needle branches in a star shape"
                ),
                "desc": "An evergreen pine tree.",
            },
        },
        "BlackberryBramble": {
            "rgb": (60, 0, 80),
            "emit_time": 40,
            "sprout_time": 25,
            "grow_time": 40,
            "lifespan_skip": 15,
            "seed": {
                "name": "Blackberry",
                "image": "blackberry",
                "prompt": "a single glossy ripe blackberry",
                "desc": "A juicy blackberry.",
            },
            "sapling": {
                "name": "BrambleSprout",
                "image": "bramble_sprout",
                "prompt": "a young thorny bramble shoot with serrated leaves",
                "desc": "A young bramble shoot.",
            },
            "plant": {
                "name": "BlackberryBramble",
                "image": "blackberry_bramble",
                "prompt": (
                    "a thorny blackberry bramble bush with white flowers and"
                    " clusters of black and red berries"
                ),
                "desc": "A thorny bramble full of blackberries.",
            },
        },
        "Strawberry": {
            "rgb": (255, 50, 80),
            "emit_time": 35,
            "sprout_time": 25,
            "grow_time": 35,
            "lifespan_skip": 12,
            "seed": {
                "name": "Strawberry",
                "image": "strawberry",
                "prompt": "a single ripe red strawberry with a green leafy cap",
                "desc": "A sweet strawberry covered in tiny seeds.",
            },
            "sapling": {
                "name": "StrawberryRunner",
                "image": "strawberry_runner",
                "prompt": "a small strawberry plantlet with three toothed leaves",
                "desc": "A strawberry runner taking root.",
            },
            "plant": {
                "name": "StrawberryPatch",
                "image": "strawberry_patch",
                "prompt": (
                    "a low strawberry plant with toothed green leaves, small white"
                    " flowers and red strawberries"
                ),
                "desc": "A strawberry patch.",
            },
        },
        "HazelBush": {
            "rgb": (160, 110, 50),
            "emit_time": 55,
            "sprout_time": 30,
            "grow_time": 50,
            "lifespan_skip": 20,
            "seed": {
                "name": "Hazelnut",
                "image": "hazelnut",
                "prompt": "a single brown hazelnut in its frilly green husk",
                "desc": "A hazelnut.",
            },
            "sapling": {
                "name": "HazelSapling",
                "image": "hazel_sapling",
                "prompt": "a young hazel sapling with round serrated leaves",
                "desc": "A young hazel.",
            },
            "plant": {
                "name": "HazelBush",
                "image": "hazel_bush",
                "prompt": (
                    "a dense round hazel bush with broad green leaves and clusters"
                    " of hazelnuts"
                ),
                "desc": "A hazel bush dropping nuts.",
            },
        },
        "Wheat": {
            "rgb": (230, 190, 90),
            "emit_time": 35,
            "sprout_time": 25,
            "grow_time": 35,
            "lifespan_skip": 10,
            "seed": {
                "name": "WheatGrain",
                "image": "wheat_grain",
                "prompt": "a small pile of golden wheat grains",
                "desc": "Wheat grains.",
            },
            "sapling": {
                "name": "WheatSprout",
                "image": "wheat_sprout",
                "prompt": "a tuft of young bright green wheat sprouts",
                "desc": "Young wheat.",
            },
            "plant": {
                "name": "WheatStalks",
                "image": "wheat_stalks",
                "prompt": "a clump of ripe golden wheat stalks with heavy ears",
                "desc": "Ripe wheat.",
            },
        },
        "Lotus": {
            "rgb": (255, 150, 200),
            "emit_time": 50,
            "sprout_time": 30,
            "grow_time": 40,
            "lifespan_skip": 15,
            "seed": {
                "name": "LotusSeed",
                "image": "lotus_seed",
                "prompt": "a green lotus seed pod with round holes",
                "desc": "A lotus seed pod.",
            },
            "sapling": {
                "name": "LotusBud",
                "image": "lotus_bud",
                "prompt": (
                    "a closed pink lotus bud on a round lily pad floating in a small"
                    " pool of water"
                ),
                "desc": "A lotus bud on a lily pad.",
            },
            "plant": {
                "name": "LotusFlower",
                "image": "lotus_flower",
                "prompt": (
                    "an open pink lotus flower on large round lily pads floating in a"
                    " small pool of water"
                ),
                "desc": "A blooming lotus.",
            },
        },
        "Moss": {
            "rgb": (90, 140, 40),
            "emit_time": 40,
            "sprout_time": 25,
            "grow_time": 35,
            "lifespan_skip": 15,
            "seed": {
                "name": "MossSpore",
                "image": "moss_spore",
                "prompt": "a small pebble with a few tiny green moss spore capsules",
                "desc": "Moss spores on a pebble.",
            },
            "sapling": {
                "name": "MossTuft",
                "image": "moss_tuft",
                "prompt": "a small grey stone with a soft green moss tuft on top",
                "desc": "A stone with a young moss tuft.",
            },
            "plant": {
                "name": "MossCarpet",
                "image": "moss_carpet",
                "prompt": (
                    "a cluster of round grey stones covered by a thick velvety green"
                    " moss carpet"
                ),
                "desc": "Mossy stones. Snails and deer graze here.",
            },
        },
        "LivingStones": {
            "rgb": (190, 170, 150),
            "emit_time": 70,
            "sprout_time": 35,
            "grow_time": 50,
            "lifespan_skip": 25,
            "seed": {
                "name": "LithopsSeed",
                "image": "lithops_seed",
                "prompt": "a tiny dried lithops seed capsule shaped like a pebble",
                "desc": "A seed of the living stones.",
            },
            "sapling": {
                "name": "LithopsSprout",
                "image": "lithops_sprout",
                "prompt": (
                    "two tiny pebble-like lithops leaves poking out of sand among"
                    " small stones"
                ),
                "desc": "A young living stone.",
            },
            "plant": {
                "name": "LivingStones",
                "image": "living_stones",
                "prompt": (
                    "a cluster of lithops living stones succulents that look like"
                    " round grey and beige pebbles with a white daisy flower"
                ),
                "desc": (
                    "Succulents disguised as stones. Only tortoises see through it."
                ),
            },
        },
        "SaltDeposit": {
            "rgb": (240, 240, 255),
            "emit_time": 80,
            "sprout_time": 40,
            "grow_time": 60,
            "lifespan_skip": 30,
            "seed": {
                "name": "SaltGrain",
                "image": "salt_grain",
                "prompt": "a few small sparkling white salt crystal grains",
                "desc": "Salt grains. Chickens peck them as grit.",
            },
            "sapling": {
                "name": "SaltCrystal",
                "image": "salt_crystal",
                "prompt": "a growing cubic white salt crystal on a flat grey stone",
                "desc": "A growing salt crystal.",
            },
            "plant": {
                "name": "SaltDeposit",
                "image": "salt_deposit",
                "prompt": (
                    "a white and pale pink mineral salt rock deposit with cubic"
                    " crystals"
                ),
                "desc": (
                    "A mineral salt lick. It slowly grows crystals and erodes."
                    " Deer and cows lick it."
                ),
            },
        },
    }
)

# ---------------------------------------------------------------------------
# Inanimate objects: passive obstacles that shape the terrain.
# ---------------------------------------------------------------------------
INANIMATE = {
    "Stone": {
        "image": "stone",
        "rgb": (153, 153, 153),
        "prompt": "a grey stone",
        "desc": (
            "A stone is just passively siting in one place and acts as an obstacle."
        ),
    },
    "Stone2": {
        "image": "stone2",
        "rgb": (153, 153, 153),
        "prompt": "a grey stone",
        "desc": (
            "A stone is just passively siting in one place and acts as an obstacle."
        ),
    },
    "FallenLog": {
        "image": "fallen_log",
        "rgb": (110, 70, 30),
        "prompt": "a fallen mossy tree log lying on the ground",
        "desc": "A fallen log blocking the way.",
    },
    "TreeStump": {
        "image": "tree_stump",
        "rgb": (140, 90, 40),
        "prompt": "an old tree stump with visible growth rings and roots",
        "desc": "An old tree stump.",
    },
    "MossyBoulder": {
        "image": "mossy_boulder",
        "rgb": (100, 120, 100),
        "prompt": "a large grey boulder partially covered in green moss",
        "desc": "A heavy mossy boulder.",
    },
    "Puddle": {
        "image": "puddle",
        "rgb": (80, 150, 220),
        "prompt": "a small shallow puddle of clear blue water with a few pebbles",
        "desc": "A small puddle of water.",
    },
    "CrystalCluster": {
        "image": "crystal_cluster",
        "rgb": (150, 100, 255),
        "prompt": "a cluster of glowing purple amethyst crystals growing out of a rock",
        "desc": "A mysterious glowing crystal cluster.",
    },
    "HayBale": {
        "image": "hay_bale",
        "rgb": (230, 200, 90),
        "prompt": "a round golden hay bale",
        "desc": "A hay bale left by a farmer.",
    },
    "WoodenBarrel": {
        "image": "wooden_barrel",
        "rgb": (150, 100, 60),
        "prompt": "an old wooden barrel with iron rings",
        "desc": "An old wooden barrel.",
    },
    "Anthill": {
        "image": "anthill",
        "rgb": (170, 110, 60),
        "prompt": (
            "a cone shaped anthill of reddish soil and pine needles with tiny ants"
        ),
        "desc": "A busy anthill.",
    },
    "Scarecrow": {
        "image": "scarecrow",
        "rgb": (200, 160, 80),
        "prompt": "a scarecrow with a straw hat, patched shirt and outstretched arms",
        "desc": "A scarecrow guarding the fields.",
    },
    "StoneWell": {
        "image": "stone_well",
        "rgb": (130, 130, 140),
        "prompt": "a round old stone water well with a small wooden roof",
        "desc": "An old stone well.",
    },
    "Signpost": {
        "image": "signpost",
        "rgb": (120, 80, 40),
        "prompt": (
            "a wooden signpost with arrow shaped signs pointing in different directions"
        ),
        "desc": "A wooden signpost.",
    },
}


def new_type_names():
    names = []
    for spec in ANIMALS.values():
        names += [s["name"] for s in spec["stages"]]
    for spec in PLANTS.values():
        names += [spec["seed"]["name"], spec["plant"]["name"]]
        if "sapling" in spec:
            names.append(spec["sapling"]["name"])
    names += list(INANIMATE)
    existing_types = {
        "Seed",
        "Seed2",
        "Seed3",
        "Grass",
        "Grass2",
        "Grass3",
        "Stone",
        "Stone2",
        "Chicken",
        "Cow",
        "Fox",
        "Badger",
        "ChickenEgg",
        "CowEgg",
        "FoxEgg",
        "BadgerEgg",
    }
    return [name for name in names if name not in existing_types]
