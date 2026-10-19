
class WAX_NetField : JsonApiStruct
{
	string path;
	string field;
	string valueType;
	string status;
	string value;
	bool directlySet;
	void WAX_NetField()
	{
		RegV("path"); RegV("field"); RegV("valueType");
		RegV("status"); RegV("value"); RegV("directlySet");
	}
	override void OnPack()
	{
		StoreString("path", path); StoreString("field", field);
		StoreString("valueType", valueType); StoreString("status", status);
		StoreString("value", value); StoreBoolean("directlySet", directlySet);
	}
}
// Workbench-only endpoint. No gameplay access, file writes or editor mutations.
class WAX_ReadOnlyNetRequest : JsonApiStruct
{
	string nonce;
	void WAX_ReadOnlyNetRequest()
	{
		RegV("nonce");
	}
}

class WAX_NetEntity : JsonApiStruct
{
	string endpoint;
	string nonce;
	string scope;
	bool editorAvailable;
	string worldPath;
	int selectedCount;
	string firstSelectedName;
	string selectedClass;
	string selectedSourceResource;
	ref array<string> ancestorResources = new array<string>();
	ref array<string> componentClasses = new array<string>();
	int componentCount;
	bool componentListTruncated;
	ref array<string> configurationRows = new array<string>();
	ref array<ref WAX_NetField> fields = new array<ref WAX_NetField>();
	void WAX_ReadOnlyNetResponse()
	{
		RegV("endpoint");
		RegV("nonce");
		RegV("scope");
		RegV("editorAvailable");
		RegV("worldPath");
		RegV("selectedCount");
		RegV("firstSelectedName");
		RegV("selectedClass");
		RegV("selectedSourceResource");
		RegV("ancestorResources");
		RegV("componentClasses");
		RegV("componentCount");
		RegV("componentListTruncated");
		RegV("configurationRows");
	}
	override void OnPack()
	{
		StoreString("firstSelectedName", firstSelectedName);
		StoreString("selectedClass", selectedClass);
		StoreString("selectedSourceResource", selectedSourceResource);
		StoreString("worldPath", worldPath);
		StoreInteger("componentCount", componentCount);
		StoreBoolean("componentListTruncated", componentListTruncated);
		StartArray("componentClasses");
		foreach (string componentClass : componentClasses)
			ItemString(componentClass);
		EndArray();
		StartArray("ancestorResources");
		foreach (string ancestorResource : ancestorResources)
			ItemString(ancestorResource);
		EndArray();
		StartArray("configurationRows");
		foreach (string row : configurationRows)
			ItemString(row);
		EndArray();
		StartArray("fields");
		foreach (WAX_NetField record : fields)
			ItemObject(record);
		EndArray();
	}
}


class WAX_ReadOnlyNetResponse : JsonApiStruct
{
	string endpoint = "WAX_ReadOnlyNetApi/v8";
	string nonce;
	string scope = "editor-configuration-not-runtime";
	int selectedCount;
	bool truncated;
	ref array<ref WAX_NetEntity> entities = new array<ref WAX_NetEntity>();
	void WAX_ReadOnlyNetResponse()
	{
		RegV("endpoint"); RegV("nonce"); RegV("scope");
		RegV("selectedCount"); RegV("truncated");
	}
	override void OnPack()
	{
		StartArray("entities");
		foreach (WAX_NetEntity entity : entities)
			ItemObject(entity);
		EndArray();
	}
}

class WAX_ReadOnlyNetApi : NetApiHandler
{
	protected void ReadField(BaseContainer node, string path, string key, string kind, WAX_NetEntity response)
	{
		WAX_NetField record = new WAX_NetField();
		record.path = path; record.field = key; record.valueType = kind; record.status = "absent";
		if (node.GetVarIndex(key) >= 0)
		{
			record.status = "read-failed";
			record.directlySet = node.IsVariableSetDirectly(key);
			bool success;
			if (kind == "bool")
			{
				bool b;
				success = node.Get(key, b);
				if (success) record.value = string.Format("%1", b);
			}
			else if (kind == "int")
			{
				int n;
				success = node.Get(key, n);
				if (success) record.value = string.Format("%1", n);
			}
			else if (kind == "string")
			{
				string textValue;
				success = node.Get(key, textValue);
				if (success) record.value = textValue;
			}
			else if (kind == "float")
			{
				float floatValue;
				success = node.Get(key, floatValue);
				if (success) record.value = string.Format("%1", floatValue);
			}
			else if (kind == "scalar-array")
			{
				array<float> scalarValues = {};
				success = node.Get(key, scalarValues);
				if (success)
				{
					record.value = string.Format("count=%1;", scalarValues.Count());
					for (int si = 0; si < scalarValues.Count() && si < 256; si++)
						record.value += string.Format(" %1", scalarValues[si]);
					if (scalarValues.Count() > 256) record.value += " TRUNCATED";
				}
			}
			else if (kind == "vector-array")
			{
				array<vector> vectorValues = {};
				success = node.Get(key, vectorValues);
				if (success)
				{
					record.value = string.Format("count=%1;", vectorValues.Count());
					for (int vi = 0; vi < vectorValues.Count() && vi < 256; vi++)
						record.value += string.Format(" %1", vectorValues[vi]);
					if (vectorValues.Count() > 256) record.value += " TRUNCATED";
				}
			}
			else if (kind == "vector")
			{
				vector vectorValue;
				success = node.Get(key, vectorValue);
				if (success) record.value = string.Format("%1", vectorValue);
			}
			else
			{
				ResourceName resource;
				success = node.Get(key, resource);
				if (success) record.value = resource;
			}
			if (success) record.status = "ok";
		}
		response.fields.Insert(record);
	}
	protected void ReadSpawnStructure(BaseContainer node, string path, int depth, WAX_NetEntity response)
	{
		if (!node || depth > 5 || response.fields.Count() >= 1500)
			return;
		response.configurationRows.Insert(path + " class=" + node.GetClassName());
		for (int index = 0; index < node.GetNumVars() && index < 128; index++)
		{
			string key = node.GetVarName(index);
			DataVarType fieldType = node.GetDataVarType(index);
			if (fieldType == DataVarType.SCALAR_ARRAY)
				ReadField(node, path, key, "scalar-array", response);
			else if (fieldType == DataVarType.VECTOR2_ARRAY || fieldType == DataVarType.VECTOR3_ARRAY)
				ReadField(node, path, key, "vector-array", response);
			else if (fieldType == DataVarType.RESOURCE_NAME)
				ReadField(node, path, key, "resource", response);
			else if (fieldType == DataVarType.OBJECT)
				ReadSpawnStructure(node.GetObject(key), path + "/" + key, depth + 1, response);
			else if (fieldType == DataVarType.OBJECT_ARRAY)
			{
				BaseContainerList children = node.GetObjectArray(key);
				if (!children) continue;
				for (int child = 0; child < children.Count() && child < 32; child++)
					ReadSpawnStructure(children.Get(child), string.Format("%1/%2[%3]", path, key, child), depth + 1, response);
			}
			else if (node.IsType(key, bool)) ReadField(node, path, key, "bool", response);
			else if (node.IsType(key, int)) ReadField(node, path, key, "int", response);
			else if (node.IsType(key, float)) ReadField(node, path, key, "float", response);
			else if (node.IsType(key, ResourceName)) ReadField(node, path, key, "resource", response);
			else if (node.IsType(key, string)) ReadField(node, path, key, "string", response);
			else if (node.IsType(key, vector)) ReadField(node, path, key, "vector", response);
			else response.configurationRows.Insert(string.Format("%1/%2 unread_type=%3", path, key, fieldType));
		}
	}
	// Bounded traversal of known configuration paths only. No runtime setters.
	protected void ReadConfiguration(BaseContainer node, string path, int depth, WAX_NetEntity response)
	{
		if (!node || depth > 6 || response.configurationRows.Count() >= 200)
			return;
		response.configurationRows.Insert(path + " class=" + node.GetClassName());
		if (node.GetClassName() == "SCR_RespawnSystemComponent")
			ReadSpawnStructure(node, path + "/spawn", 0, response);
		// Inspect actual editor values, including inherited recoil and sway data.
		// The existing bounded reader only calls getters.
		string configClass = node.GetClassName();
		if (configClass == "RecoilWeaponAimModifier" || configClass == "SwayWeaponAimModifier" || configClass == "SCR_RecoilCameraShakeParams")
			ReadSpawnStructure(node, path + "/aim", 0, response);
		array<string> boolFields = {"m_bNativeDoubleBarrelReload", "m_bG3B2WriteEnabled", "m_bG3B2InventoryWide", "m_bG3B2MultiplePacks", "BindWithInjection"};
		foreach (string boolField : boolFields)
		{
			ReadField(node, path, boolField, "bool", response);
			bool boolValue;
			if (node.GetVarIndex(boolField) >= 0 && node.Get(boolField, boolValue))
				response.configurationRows.Insert(string.Format("%1 %2=%3", path, boolField, boolValue));
		}
		array<string> intFields = {"m_iTubeCapacity", "m_iLoadedCapacity", "m_iG3B2RequiredTargetMax", "m_iT4BStartAmmo"};
		foreach (string intField : intFields)
		{
			ReadField(node, path, intField, "int", response);
			int intValue;
			if (node.GetVarIndex(intField) >= 0 && node.Get(intField, intValue))
				response.configurationRows.Insert(string.Format("%1 %2=%3", path, intField, intValue));
		}
		array<string> resourceFields = {"AnimGraph", "AnimInstance", "MagazineTemplate"};
		foreach (string resourceField : resourceFields)
		{
			ReadField(node, path, resourceField, "resource", response);
			ResourceName resourceValue;
			if (node.GetVarIndex(resourceField) >= 0 && node.Get(resourceField, resourceValue))
				response.configurationRows.Insert(path + " " + resourceField + "=" + resourceValue);
		}
		array<string> arrayFields = {"components", "additionalActions", "WeaponAimModifiers", "CustomAttributes"};
		foreach (string arrayField : arrayFields)
		{
			if (node.GetVarIndex(arrayField) < 0)
				continue;
			BaseContainerList children = node.GetObjectArray(arrayField);
			if (!children)
				continue;
			for (int n = 0; n < children.Count() && n < 64; n++)
				ReadConfiguration(children.Get(n), string.Format("%1/%2[%3]", path, arrayField, n), depth + 1, response);
		}
		if (node.GetVarIndex("AnimInjection") >= 0)
			ReadConfiguration(node.GetObject("AnimInjection"), path + "/AnimInjection", depth + 1, response);
		if (node.GetVarIndex("Attributes") >= 0)
			ReadConfiguration(node.GetObject("Attributes"), path + "/Attributes", depth + 1, response);
	}

	override JsonApiStruct GetRequest()
	{
		return new WAX_ReadOnlyNetRequest();
	}

	protected WAX_NetEntity ReadSelected(WorldEditorAPI selectionApi, int selectionIndex)
	{
		
		WAX_NetEntity response = new WAX_NetEntity();
		response.endpoint = "WAX_ReadOnlyNetApi/v4";
		response.scope = "editor-context-only-not-gameplay";
		WorldEditor editor = Workbench.GetModule(WorldEditor);
		if (editor)
		{
			WorldEditorAPI api = editor.GetApi();
			if (api)
			{
				response.editorAvailable = true;
				api.GetWorldPath(response.worldPath);
				response.selectedCount = api.GetSelectedEntitiesCount();
				if (response.selectedCount > 0)
				{
					IEntitySource selected = api.GetSelectedEntity(selectionIndex);
					if (selected)
					{
						response.firstSelectedName = api.GetEntityNiceName(selected);
						response.selectedClass = selected.GetClassName();
						if (selected.GetClassName() == "SCR_LoadoutManager")
							ReadSpawnStructure(selected, "loadouts", 0, response);
						response.selectedSourceResource = selected.GetResourceName();
						BaseContainer ancestor = selected.GetAncestor();
						for (int depth = 0; ancestor && depth < 16; depth++)
						{
							response.ancestorResources.Insert(ancestor.GetResourceName());
							ancestor = ancestor.GetAncestor();
						}
						response.componentCount = selected.GetComponentCount();
						response.componentListTruncated = response.componentCount > 128;
						for (int i = 0; i < response.componentCount && i < 128; i++)
						{
							IEntityComponentSource component = selected.GetComponent(i);
							if (component)
							{
								response.componentClasses.Insert(component.GetClassName());
								ReadConfiguration(component, string.Format("component[%1]", i), 0, response);
							}
						}
					}
				}
			}
		}

		return response;
	}

	override JsonApiStruct GetResponse(JsonApiStruct request)
	{
		WAX_ReadOnlyNetResponse response = new WAX_ReadOnlyNetResponse();
		WAX_ReadOnlyNetRequest req = WAX_ReadOnlyNetRequest.Cast(request);
		if (req) response.nonce = req.nonce;
		WorldEditor editor = Workbench.GetModule(WorldEditor);
		if (!editor) return response;
		WorldEditorAPI api = editor.GetApi();
		if (!api) return response;
		response.selectedCount = api.GetSelectedEntitiesCount();
		response.truncated = response.selectedCount > 8;
		for (int index = 0; index < response.selectedCount && index < 8; index++)
			response.entities.Insert(ReadSelected(api, index));
		return response;
	}
}
