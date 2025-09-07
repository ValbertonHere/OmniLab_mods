from vehicle_systems import model_assembler

engineEventsOverrides = {'eng_V2K': 'eng_v55', 'eng_V2_34': 'eng_v55', 'eng_Continental_R975_C1': 'eng_Continental_R975'}

def returnToMonke(isPlayer, appearance):
    typeDescriptor = appearance.typeDescriptor
    sounds = list(typeDescriptor.engine.sounds._WWTripleSoundConfig__eventNames)
    for idx, event in enumerate(sounds):
        for oldEvent in engineEventsOverrides.keys():
            if event.find(oldEvent) != -1:
                sounds[idx] = event.replace(oldEvent, engineEventsOverrides[oldEvent])
                break
    
    typeDescriptor.engine.sounds._WWTripleSoundConfig__eventNames = tuple(sounds)
    base(isPlayer, appearance)

base = model_assembler.assembleVehicleAudition
model_assembler.assembleVehicleAudition = returnToMonke