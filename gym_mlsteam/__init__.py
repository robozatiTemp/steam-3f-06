from gym.envs.registration import register

register(
    id='mlsteam-v0',
    entry_point='gym_mlsteam.envs:MlSteamEnv001',
)

register(
    id='mlsteam-v1',
    entry_point='gym_mlsteam.envs:MlSteamEnv002',
)