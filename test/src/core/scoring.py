from src import config


class ScoreCalculator:

    @staticmethod
    def score_for_distance(distance):
        ratio = distance / config.MAX_SCORING_DISTANCE
        if ratio > 1.0:
            ratio = 1.0

        score_range = config.MAX_TARGET_SCORE - config.MIN_TARGET_SCORE
        raw_score = config.MIN_TARGET_SCORE + ratio * score_range
        return int(round(raw_score))

    @staticmethod
    def combo_bonus(streak_after_this_hit):
        if streak_after_this_hit >= config.COMBO_MIN_STREAK:
            return config.COMBO_BONUS
        return 0

    @classmethod
    def total_for_hit(cls, distance, streak_after_this_hit):
        distance_score = cls.score_for_distance(distance)
        bonus = cls.combo_bonus(streak_after_this_hit)
        return distance_score + bonus
