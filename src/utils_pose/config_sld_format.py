format_example = """
[
    {
        "input_fname": "dalle3_banana",
        "output_dir": "dalle3_banana",
        "prompt": "Replace the left apple with a pumpkin and keep the right apple and all bananas in the scene unchanged",
        "generator": "dalle",
        "llm_parsed_prompt":{
            "objects": [
                ["apple", [null, null]],
                ["banana", [null]],
                ["pumpkin", [null]]
            ],
            "bg_prompt": "A realistic image",
            "neg_prompt": null
        },
        "llm_layout_suggestions": [
            ["pumpkin #1", [0.177, 0.567, 0.243, 0.246]], 
            ["apple #2", [0.416, 0.579, 0.239, 0.256]], 
            ["banana #1", [0.473, 0.235, 0.485, 0.504]], 
            ["banana #2", [0.293, 0.199, 0.218, 0.464]], 
            ["banana #3", [0.255, 0.202, 0.185, 0.379]], 
            ["banana #4", [0.64, 0.701, 0.172, 0.099]], 
            ["banana #5", [0.303, 0.213, 0.527, 0.583]], 
            ["banana #6", [0.419, 0.283, 0.126, 0.321]]
        ]
    },
    {
        "input_fname": "dalle3_dog",
        "output_dir": "dalle3_dog",
        "prompt": "Make the dog a sleeping dog and remove all shadows in an image of a grassland",
        "generator": "dalle",
        "llm_parsed_prompt":{
            "objects": [["dog", ["sleeping"]], ["shadows", [null]]],
            "bg_prompt": "A realistic image of a grassland",
            "neg_prompt": "shadows"
        },
        "llm_layout_suggestions": [["sleeping dog #1", [0.172, 0.15, 0.761, 0.577]]]
    },
    {
        "input_fname": "indoor_scene",
        "output_dir": "indoor_scene_move",
        "prompt": "Shift the dog slightly upward and move the cat slightly towards the dog in a window-view image of an urban landscape.",
        "generator": "dalle",
        "llm_parsed_prompt":{
            "objects": [["dog", [null]], ["cat", [null]]],
            "bg_prompt": "A window-view image of an urban landscape",
            "neg_prompt": null
        },
        "llm_layout_suggestions": [["dog #1", [0.003, 0.209, 0.447, 0.62]], ["cat #1", [0.457, 0.342, 0.441, 0.595]]]
    },
    {
        "input_fname": "indoor_scene",
        "output_dir": "indoor_scene_swap",
        "prompt": "Exchange the position of the black dog and yellow cat in a window-view image of an urban landscape. Keep their original shape.",
        "generator": "dalle",
        "llm_parsed_prompt":{
            "objects": [["dog", ["black"]], ["cat", ["yellow"]]],
            "bg_prompt": "A window-view image of an urban landscape",
            "neg_prompt": null
        },
        "llm_layout_suggestions": [["yellow cat #1", [0.003, 0.309, 0.441, 0.595]], ["black dog #1", [0.557, 0.342, 0.447, 0.62]]]
    },
    {
        "input_fname": "indoor_scene",
        "output_dir": "indoor_scene_attr_mod",
        "prompt": "Transform the dog into a robotic dog and the cat into a sculptural cat in a window-view image of an urban landscape",
        "generator": "dalle",
        "llm_parsed_prompt":{
            "objects": [["dog", [null]], ["cat", [null]]],
            "bg_prompt": "A window-view image of an urban landscape",
            "neg_prompt": null
        },
        "llm_layout_suggestions": [["robotic dog #1", [0.003, 0.309, 0.447, 0.62]], ["sculptural cat #1", [0.557, 0.342, 0.441, 0.595]]]
    },
    {
        "input_fname": "indoor_scene",
        "output_dir": "indoor_scene_resize",
        "prompt": "Slightly increase the cat's size and reduce the dog's size in a window-view image of an urban landscape. Keep their bottom unchanged.",
        "generator": "dalle",
        "llm_parsed_prompt":{
            "objects": [["dog", [null]], ["cat", [null]]],
            "bg_prompt": "A window-view image of an urban landscape",
            "neg_prompt": null
        },
        "llm_layout_suggestions": [["dog #1", [0.103, 0.409, 0.347, 0.52]], ["cat #1", [0.457, 0.242, 0.541, 0.695]]]
    },
    {
        "input_fname": "indoor_scene",
        "output_dir": "indoor_scene_replace",
        "prompt": "Replace the dog with a houseplant and keep the cat unchanged in a window-view image of an urban landscape.",
        "generator": "dalle",
        "llm_parsed_prompt":{
            "objects": [["dog", [null]], ["cat", [null]], ["houseplant", [null]]],
            "bg_prompt": "A window-view image of an urban landscape",
            "neg_prompt": null
        },
        "llm_layout_suggestions": [["houseplant #1", [0.003, 0.309, 0.447, 0.62]], ["cat #1", [0.557, 0.342, 0.441, 0.595]]]
    },
    {
        "input_fname": "indoor_table",
        "output_dir": "indoor_table_swap",
        "prompt": "Swap the position of bowl and the cup, maintaining their original shape",
        "generator": "dalle",
        "llm_parsed_prompt":{
            "objects": [["bowl", [null]], ["cup", [null]]],
            "bg_prompt": "A realistic image",
            "neg_prompt": null
        },
        "llm_layout_suggestions": [["bowl #1", [0.483, 0.477, 0.361, 0.18]], ["cup #1", [0.08, 0.365, 0.329, 0.255]]]
    },
    {
        "input_fname": "indoor_table",
        "output_dir": "indoor_table_resize",
        "prompt": "Make the cup 1.25 times larger but keep the bowl's size unchanged",
        "generator": "dalle",
        "llm_parsed_prompt":{
            "objects": [["bowl", [null]], ["cup", [null]]],
            "bg_prompt": "A realistic image",
            "neg_prompt": null
        },
        "llm_layout_suggestions": [["bowl #1", [0.08, 0.415, 0.361, 0.18]], ["cup #1", [0.483, 0.447, 0.41125, 0.31875]]]
    },
    {
        "input_fname": "indoor_table",
        "output_dir": "indoor_table_move",
        "prompt": "Move the cup towards the bowl until they slightly overlap",
        "generator": "dalle",
        "llm_parsed_prompt":{
            "objects": [["bowl", [null]], ["cup", [null]]],
            "bg_prompt": "A realistic image",
            "neg_prompt": null
        },
        "llm_layout_suggestions": [["bowl #1", [0.08, 0.415, 0.361, 0.18]], ["cup #1", [0.413, 0.447, 0.329, 0.255]]]
    },
    {
        "input_fname": "indoor_table",
        "output_dir": "indoor_table_attr_mod",
        "prompt": "Turn the cup into green and the bowl into golden",
        "generator": "dalle",
        "llm_parsed_prompt":{
            "objects": [["bowl", [null]], ["cup", [null]]],
            "bg_prompt": "A realistic image",
            "neg_prompt": null
        },
        "llm_layout_suggestions": [["golden bowl #1", [0.08, 0.415, 0.361, 0.18]], ["green cup #1", [0.483, 0.447, 0.329, 0.255]]]
    },
    {
        "input_fname": "indoor_table",
        "output_dir": "indoor_table_replace",
        "prompt": "Replace the bowl with two round apples and keep the cup unchanged",
        "generator": "dalle",
        "llm_parsed_prompt":{
            "objects": [["bowl", [null]], ["cup", [null]], ["apple", ["round", "round"]]],
            "bg_prompt": "A realistic image",
            "neg_prompt": null
        },
        "llm_layout_suggestions": [["cup #1", [0.483, 0.447, 0.329, 0.255]], ["apple #1", [0.08, 0.415, 0.18, 0.18]], ["apple #2", [0.26, 0.415, 0.18, 0.18]]]
    }    
]
"""