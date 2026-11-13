# Create your first plugin

You do not need Rust or .NET. Open PaintFE's Script Editor, write a script, then choose **Create plugin**. The code remains in the Script Editor; **Plugin properties** describes its name, menu category, controls and artwork.

For a first effect use:

```rhai
apply_hsl(params.hue, 0.0, 0.0);
```

Add a Number parameter with ID `hue`, label `Hue`, minimum -180, maximum 180, step 1 and default 0. Configure the pack name, description, author, licence and effect category. Choose **Save locally**. It appears under Filter in the pack's category. This unsigned local copy is labelled as local.

**Save** updates the current local plugin. **Save as** creates a new identity. Use **Export** to create a `.pfeplugin` file for sharing. **Edit a local copy** on an installed community pack preserves the original and its licence.

A pack can contain multiple effects. Add an effect in Properties and select it to load its code into the existing editor. Name, category and parameter changes are saved with the pack. Test Apply, Cancel and a single Undo before submitting.

To work from files, copy `plugins/paintfe/colour-workshop` to your publisher folder, change its IDs and metadata, then run the validation commands in CONTRIBUTING.md. The examples demonstrate complete manifests and scripts.
