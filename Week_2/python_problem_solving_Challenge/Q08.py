def launch(*stages, abort_threshold = 5000):
    payload = 0
    for i, stage in enumerate(stages):
        payload += stage
        print(f'Stage {i+1} armed --> cumulative {payload} kg')
        if payload > abort_threshold:
            print(f'[ABORT] at stage {i+1}: threshold {abort_threshold} kg exceeded.')
            break

launch(1200, 1800, 2500, 900, abort_threshold=4000)