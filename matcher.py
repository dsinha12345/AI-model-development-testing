from astrology import gun_milan
from database import cursor


def compatibility_score(guna):
    score = (
        0.25 * guna["nadi"] +
        0.20 * guna["bhakoot"] +
        0.15 * guna["gana"] +
        0.10 * guna["graha_maitri"] +
        0.30 * (guna["varna"] + guna["vashya"] + guna["tara"] + guna["yoni"])
    )

    # Correct max = 7.8
    return round((score / 7.8) * 10, 1)


def match_users():
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    results = []

    for i in range(len(users)):
        for j in range(i + 1, len(users)):
            guna = gun_milan(users[i], users[j])
            score = compatibility_score(guna)

            results.append({
                "user1": users[i][1],
                "user2": users[j][1],
                "guna_total": guna["total"],
                "compatibility": score,
                "details": guna
            })

    return sorted(results, key=lambda x: x["compatibility"], reverse=True)