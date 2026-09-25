// reports/samples/ARMST_BallisticRangeProbe.c
//
// Experimental Workbench/runtime helper for reading the maximum direct-fire
// range represented by the ballistic table of the NEXT projectile in a muzzle.
//
// Status:
// - API contract is source-backed by Bohemia Interactive documentation.
// - This sample has NOT yet been compiled or runtime-validated in ARMST Workbench.
// - Do not treat its output as gameplay policy until Workbench validation.
//
// BallisticTable.GetAimHeightOfNextProjectile() returns a negative time when the
// requested distance is farther than the projectile's maximum ballistic-table
// range. We use that boundary to find the largest supported distance.
//
// IMPORTANT:
// - This is NOT sight zeroing range.
// - This is NOT DispersionRange.
// - This is NOT "effective combat range" or lethality range.
// - The result depends on the next projectile selected by the muzzle and the
//   muzzle's bullet-init-speed coefficient.

class ARMST_BallisticRangeProbe
{
	static const float RESULT_INVALID_INPUT = -1.0;
	static const float RESULT_LIMIT_NOT_REACHED = -2.0;

	// Returns the largest distance (metres) that is still inside the current
	// direct-fire ballistic table.
	//
	// RESULT_INVALID_INPUT (-1):
	//   invalid muzzle or invalid search parameters.
	//
	// RESULT_LIMIT_NOT_REACHED (-2):
	//   no out-of-range boundary was found before probeLimitMeters.
	static float FindMaxDirectFireRange(
		BaseMuzzleComponent muzzleComp,
		float coarseStepMeters = 100.0,
		float precisionMeters = 1.0,
		float probeLimitMeters = 20000.0)
	{
		if (!muzzleComp)
			return RESULT_INVALID_INPUT;

		if (coarseStepMeters <= 0.0 || precisionMeters <= 0.0 || probeLimitMeters <= 0.0)
			return RESULT_INVALID_INPUT;

		if (precisionMeters >= coarseStepMeters)
			return RESULT_INVALID_INPUT;

		float time;
		float low = 0.0;
		float high = -1.0;

		// Coarse pass: find the first distance that lies outside the table.
		for (float distance = coarseStepMeters; distance <= probeLimitMeters; distance += coarseStepMeters)
		{
			BallisticTable.GetAimHeightOfNextProjectile(distance, time, muzzleComp, true);

			if (time < 0.0)
			{
				high = distance;
				break;
			}

			low = distance;
		}

		if (high < 0.0)
			return RESULT_LIMIT_NOT_REACHED;

		// Fine pass: binary-search the in-range / out-of-range boundary.
		while ((high - low) > precisionMeters)
		{
			float mid = (low + high) * 0.5;

			BallisticTable.GetAimHeightOfNextProjectile(mid, time, muzzleComp, true);

			if (time < 0.0)
				high = mid;
			else
				low = mid;
		}

		return low;
	}

	static void LogMaxDirectFireRange(
		BaseMuzzleComponent muzzleComp,
		float coarseStepMeters = 100.0,
		float precisionMeters = 1.0,
		float probeLimitMeters = 20000.0)
	{
		float range = FindMaxDirectFireRange(
			muzzleComp,
			coarseStepMeters,
			precisionMeters,
			probeLimitMeters);

		if (range == RESULT_INVALID_INPUT)
		{
			Print("[ARMST BallisticRangeProbe] Invalid input.");
			return;
		}

		if (range == RESULT_LIMIT_NOT_REACHED)
		{
			PrintFormat(
				"[ARMST BallisticRangeProbe] No ballistic-table limit found below %1 m.",
				probeLimitMeters);
			return;
		}

		PrintFormat(
			"[ARMST BallisticRangeProbe] Max direct-fire ballistic-table range: %1 m; muzzle init-speed coef: %2",
			range,
			muzzleComp.GetBulletInitSpeedCoef());
	}
};
