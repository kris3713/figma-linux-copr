%global         __provides_exclude_from ^/opt/%{full_name}/.*$
%global         __requires_exclude_from ^/opt/%{full_name}/.*$
%global         full_name figma-linux
%global         debug_package %{nil}

Name:           figma-linux-arm64
Version:        0.11.5
Release:        1%{?dist}
Summary:        Figma-Linux is an unofficial Electron-based Figma desktop app for Linux.

License:        GPL-2.0
URL:            https://github.com/Figma-Linux/figma-linux

Source0:        https://github.com/Figma-Linux/figma-linux/releases/download/v%{version}/%{full_name}_%{version}_linux_arm64.zip
Source1:        https://raw.githubusercontent.com/Figma-Linux/figma-linux/master/resources/%{full_name}.desktop

ExclusiveArch:  %arm64

# Requires:       # Might use this later

%description
Figma is the first interface design tool based in the browser, making it easier for teams to create software.

%prep
%setup -q -c -n ./%{full_name}

%install
# Setup the buildroot
install -d %{buildroot}{/opt/%{full_name},%{_bindir},%{_datadir}/applications}

sizes=(
  '24x24' '36x36' '48x48' '64x64' '72x72' '96x96'
  '128x128' '192x192' '256x256' '384x384' '512x512'
)
for size in "${sizes[@]}"; do
  install -d "%{buildroot}%{_iconsdir}/hicolor/$size/apps"
done
install -d %{buildroot}%{_iconsdir}/hicolor/scalable/apps

# Copy the application files to the application directory
cp -a . %{buildroot}/opt/%{full_name}

# Install the desktop file
install -Dm 0644 %{SOURCE1} -t %{buildroot}%{_datadir}/applications

# Create a symlink to the application binary
ln_s /opt/figma-linux/figma-linux %{buildroot}%{_bindir}

# Install application icons
for size in "${sizes[@]}"; do
  install -Dm 0644 "$BUILD_DIR/icons/$size.png" \
    "%{buildroot}%{_iconsdir}/hicolor/$size/apps/%{name}.png"
done
install -Dm 0644 "$BUILD_DIR/icons/scalable.svg" \
  %{buildroot}%{_iconsdir}/hicolor/scalable/apps/%{name}.png

%files
/opt/%{full_name}
%{_bindir}/%{full_name}
%{_datadir}/applications/%{full_name}.desktop
%{_iconsdir}/hicolor/*/apps/%{name}.png

%changelog
%autochangelog
